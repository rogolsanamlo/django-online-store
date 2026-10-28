/*
 * Shop actions: add to cart, toggle favourite, add to compare list.
 *
 * Buttons declare what they do with data attributes, e.g.
 *   <button data-action="add-to-cart" data-product-id="5" data-qty="1">
 * One delegated click handler does the work, so it keeps working for cards that
 * are cloned or inserted later, and it does not depend on any other script.
 */
(function () {
  'use strict';

  var CART_COUNT_SELECTOR = '#indicator__value';

  function showMessage(text, isError) {
    var box = document.createElement('div');
    box.className = 'shop-toast' + (isError ? ' shop-toast--error' : '');
    box.textContent = text;
    document.body.appendChild(box);
    setTimeout(function () { box.classList.add('shop-toast--visible'); }, 10);
    setTimeout(function () {
      box.classList.remove('shop-toast--visible');
      setTimeout(function () { box.remove(); }, 300);
    }, 3000);
  }

  function get(url, params) {
    var query = new URLSearchParams(params || {}).toString();
    return fetch(url + (query ? '?' + query : ''), { credentials: 'same-origin' }).then(function (response) {
      return response.text().then(function (text) {
        return { ok: response.ok, status: response.status, text: text };
      });
    });
  }

  function post(url, params) {
    var meta = document.querySelector('meta[name="csrf-token"]');
    var body = new URLSearchParams(params || {});
    return fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'X-CSRFToken': meta ? meta.content : '', 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString()
    }).then(function (response) {
      return response.text().then(function (text) {
        return { ok: response.ok, status: response.status, text: text };
      });
    });
  }

  function failed(result, fallbackMessage) {
    var detail = result.status === 401 && result.text ? result.text : fallbackMessage + ' (کد خطا ' + result.status + ')';
    showMessage(detail, true);
  }

  function networkError() {
    showMessage('ارتباط با سرور برقرار نشد', true);
  }

  function setCartCount(value) {
    var element = document.querySelector(CART_COUNT_SELECTOR);
    if (element) { element.textContent = value; }
  }

  function setCompareCount(value) {
    var element = document.querySelector('#compare_count');
    if (!element) { return; }
    element.textContent = value;
    element.style.display = String(value).trim() === '0' ? 'none' : '';
  }

  function refreshCompareCount() {
    get('/products/status_of_compare_list/').then(function (result) {
      if (result.ok) { setCompareCount(result.text); }
    }).catch(function () {});
  }

  function refreshCartCount() {
    get('/orders/status_of_shop_cart/').then(function (result) {
      if (result.ok) { setCartCount(result.text); }
    }).catch(function () {});
  }

  var actions = {
    'add-to-cart': function (button) {
      var qty = button.dataset.qty || 1;
      if (button.dataset.qtyInput) {
        var input = document.querySelector(button.dataset.qtyInput);
        if (input && input.value) { qty = input.value; }
      }
      get('/orders/add_to_shop_cart/', { product_id: button.dataset.productId, qty: qty }).then(function (result) {
        if (result.ok) {
          setCartCount(result.text);
          showMessage('کالا به سبد خرید اضافه شد');
        } else {
          failed(result, 'افزودن به سبد خرید انجام نشد');
        }
      }).catch(networkError);
    },

    'toggle-favorite': function (button) {
      post('/csf/toggle_favorite/', { productId: button.dataset.productId }).then(function (result) {
        if (!result.ok) {
          failed(result, 'تغییر علاقه‌مندی‌ها انجام نشد');
          return;
        }
        var data = JSON.parse(result.text);
        // the same product can appear several times on a page (new / cheapest ...): update all hearts
        var hearts = document.querySelectorAll('[data-action="toggle-favorite"]');
        for (var i = 0; i < hearts.length; i++) {
          if (hearts[i].dataset.productId !== button.dataset.productId) { continue; }
          var icon = hearts[i].querySelector('i');
          if (!icon) { continue; }
          icon.classList.remove(data.favorite ? 'far' : 'fas');
          icon.classList.add(data.favorite ? 'fas' : 'far');
        }
        showMessage(data.message);
      }).catch(networkError);
    },

    'remove-from-compare': function (button) {
      get('/products/delete_from_compare_list/', { productId: button.dataset.productId }).then(function (result) {
        if (!result.ok) {
          failed(result, 'حذف از مقایسه انجام نشد');
          return;
        }
        var container = document.querySelector('#compare_list');
        if (container) { container.innerHTML = result.text; }
        refreshCompareCount();
        showMessage('کالا از لیست مقایسه حذف شد');
      }).catch(networkError);
    },

    // tabs of the "cheapest" / "newest" blocks: reload the cards for the chosen group
    'filter-group': function (button) {
      var target = document.querySelector(button.dataset.target);
      if (!target) { return; }
      var tabs = button.closest('.block-header__groups-list').querySelectorAll('.block-header__group');
      for (var i = 0; i < tabs.length; i++) { tabs[i].classList.remove('block-header__group--active'); }
      button.classList.add('block-header__group--active');
      target.style.opacity = '0.5';
      get(button.dataset.url, { grid: 1, group: button.dataset.groupId || '' }).then(function (result) {
        target.style.opacity = '';
        if (result.ok) { target.innerHTML = result.text; } else { failed(result, 'دریافت محصولات انجام نشد'); }
      }).catch(function () { target.style.opacity = ''; networkError(); });
    },

    // "update cart" button of the cart page
    'update-cart': function () {
      var inputs = document.querySelectorAll("#shop_cart_list input[id^='qty_']");
      var ids = [];
      var qtys = [];
      for (var i = 0; i < inputs.length; i++) {
        ids.push(inputs[i].id.slice(4));
        qtys.push(inputs[i].value);
      }
      var params = new URLSearchParams();
      ids.forEach(function (id) { params.append('product_id_list[]', id); });
      qtys.forEach(function (qty) { params.append('qty_list[]', qty); });
      fetch('/orders/update_shop_cart/?' + params.toString(), { credentials: 'same-origin' }).then(function (response) {
        return response.text().then(function (text) {
          if (!response.ok) { failed({ status: response.status, text: text }, 'به‌روزرسانی سبد انجام نشد'); return; }
          document.querySelector('#shop_cart_list').innerHTML = text;
          refreshCartCount();
          showMessage('سبد خرید به‌روزرسانی شد');
        });
      }).catch(networkError);
    },

    'add-to-compare': function (button) {
      get('/products/add_to_compare_list/', {
        productId: button.dataset.productId,
        productGroupId: button.dataset.groupId || 0
      }).then(function (result) {
        if (result.ok) {
          refreshCompareCount();
          showMessage(result.text);
        } else {
          failed(result, 'افزودن به لیست مقایسه انجام نشد');
        }
      }).catch(networkError);
    }
  };

  document.addEventListener('click', function (event) {
    var button = event.target.closest('[data-action]');
    if (!button || !actions[button.dataset.action]) { return; }
    event.preventDefault();
    actions[button.dataset.action](button);
  });

  document.addEventListener('DOMContentLoaded', function () {
    refreshCartCount();
    refreshCompareCount();
  });
})();
