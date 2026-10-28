# Django Online Shop

🇮🇷 [نسخهٔ فارسی](README.fa.md)

A Persian (RTL) e-commerce web application built with Django. It started from a video course
project (a single-store shop) and was then cleaned up, fixed and extended: a working
**ZarinPal** payment flow, stock handling, a test suite and a safer configuration.

## Features

- Custom user model (login with mobile number), SMS activation (Kavenegar) and password recovery
- Product groups, brands, dynamic features and filters, price filter, sorting, pagination, compare list
- Session based shopping cart, coupons and discount baskets
- Checkout and **online payment with ZarinPal** (sandbox supported)
- Per-user payment history, payment list in the admin
- Warehouse: stock is taken out automatically, exactly once, after a verified payment
- Product comments (moderated), 0-5 ratings, favourites
- Persian Django admin with CKEditor for rich-text descriptions

## Screenshots

### Shopping
<table>
  <tr>
    <td align="center"><img src="docs/screenshots/01-home.png" alt="Home page with the category mega menu"><br><sub>Home page with the category mega menu</sub></td>
    <td align="center"><img src="docs/screenshots/02-product-cards.png" alt="Product cards: add to cart, favourites, compare"><br><sub>Product cards: add to cart, favourites, compare</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/03-categories.png" alt="Popular categories and newest products"><br><sub>Popular categories and newest products</sub></td>
    <td align="center"><img src="docs/screenshots/04-product-details.png" alt="Product details, rating and brand"><br><sub>Product details, rating and brand</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/05-reviews.png" alt="Customer reviews (moderated)"><br><sub>Customer reviews (moderated)</sub></td>
    <td align="center"><img src="docs/screenshots/06-compare.png" alt="Product comparison table"><br><sub>Product comparison table</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/07-favorites.png" alt="Favourites list"><br><sub>Favourites list</sub></td>
    <td align="center"><img src="docs/screenshots/10-cart.png" alt="Shopping cart"><br><sub>Shopping cart</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/11-cart-summary.png" alt="Cart totals: shipping and tax"><br><sub>Cart totals: shipping and tax</sub></td>
    <td align="center"><img src="docs/screenshots/12-checkout.png" alt="Checkout with coupon code"><br><sub>Checkout with coupon code</sub></td>
  </tr>
</table>

### Account and payment
<table>
  <tr>
    <td align="center"><img src="docs/screenshots/08-register.png" alt="Sign-up with mobile number"><br><sub>Sign-up with mobile number</sub></td>
    <td align="center"><img src="docs/screenshots/09-verify-mobile.png" alt="Mobile activation code"><br><sub>Mobile activation code</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/13-zarinpal-sandbox.png" alt="ZarinPal sandbox gateway"><br><sub>ZarinPal sandbox gateway</sub></td>
    <td align="center"><img src="docs/screenshots/14-payment-result.png" alt="Payment result with tracking code"><br><sub>Payment result with tracking code</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/15-my-payments.png" alt="Payment history in the user panel"><br><sub>Payment history in the user panel</sub></td>
    <td></td>
  </tr>
</table>

### User panel and pages
<table>
  <tr>
    <td align="center"><img src="docs/screenshots/25-login.png" alt="Login with mobile number"><br><sub>Login with mobile number</sub></td>
    <td align="center"><img src="docs/screenshots/26-remember-password.png" alt="Password recovery"><br><sub>Password recovery</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/22-user-panel.png" alt="User panel: profile"><br><sub>User panel: profile</sub></td>
    <td align="center"><img src="docs/screenshots/23-user-panel-orders.png" alt="User panel: recent orders"><br><sub>User panel: recent orders</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/24-change-password.png" alt="Change password"><br><sub>Change password</sub></td>
    <td align="center"><img src="docs/screenshots/19-contact.png" alt="Contact page"><br><sub>Contact page</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/20-about.png" alt="About page"><br><sub>About page</sub></td>
    <td align="center"><img src="docs/screenshots/21-terms.png" alt="Terms and conditions"><br><sub>Terms and conditions</sub></td>
  </tr>
</table>

### Admin panel
<table>
  <tr>
    <td align="center"><img src="docs/screenshots/16-admin-products.png" alt="Admin: products"><br><sub>Admin: products</sub></td>
    <td align="center"><img src="docs/screenshots/17-admin-warehouse.png" alt="Admin: warehouse entries"><br><sub>Admin: warehouse entries</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/18-admin-discount-basket.png" alt="Admin: discount baskets"><br><sub>Admin: discount baskets</sub></td>
    <td></td>
  </tr>
</table>

## What differs from the course project

The course project was the starting point; this repository changes it in these ways:

**Payments**
- The payment app of the course no longer worked with the current ZarinPal API. It was rewritten
  against the ZarinPal REST API v4 (`requests`; request, redirect, verify), It lives in `apps/payments/gateway.py`.
- Only the owner of an order can pay for it; amounts are stored in Toman and converted to Rial
  for the gateway.
- Verification is idempotent: reloading the callback never deducts stock twice
  (`select_for_update` + `transaction.atomic`).
- The result message is kept in the session, not in the URL.

**Configuration and security**
- No secrets in the repository: everything comes from environment variables (`.env.example`).
- MySQL by default, SQLite through `DB_ENGINE=sqlite`.
- Prices of an order are read from the database and frozen in the order lines.

**Code quality**
- Persian names for apps, models and fields in the admin.
- A test suite (authentication, cart and orders, payments, pages, admin) in which the
  ZarinPal API calls and SMS sending are mocked.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # then edit the values
python manage.py migrate
python manage.py seed_data                             # default payment type / order state / warehouse types
python manage.py seed_demo                             # optional: demo categories, brands and products
python manage.py createsuperuser
python manage.py runserver
```

The default database is MySQL: create an empty database first and fill in the `DB_*` variables in `.env`.
Set `DB_ENGINE=sqlite` to use a local `db.sqlite3` file instead.

### Sign-up codes in development
No SMS key is needed locally. Without a Kavenegar API key no SMS is sent and nothing is printed;
the activation code is stored in the database (`accounts_customuser.active_code`). Read it there,
or in the admin under *کاربران* → the user → `کد فعال سازی`.

## Payment flow (ZarinPal)

1. `orders:create_order` turns the session cart into an `Order` (prices are read from the DB).
2. `orders:checkout_order` collects the address and payment type and applies coupons.
3. `payments:zarinpal_payment` creates a `Payment`, requests an *authority* and redirects to the gateway.
4. The gateway redirects back to `payments:zarinpal_verify`; the payment is verified with the stored amount.
5. On success the order is marked paid, stock is deducted once and the cart is cleared.

Use `ZARINPAL_SANDBOX=True` while developing.

## Tests

```bash
python manage.py test
```

## Project layout

```
apps/
  accounts/   users, profile, SMS verification
  products/   catalogue, filters, compare
  orders/     cart, orders, coupons, checkout
  payments/   ZarinPal integration
  warehouses/ stock movements
  discounts/  coupons, discount baskets
  comment_scoring_favorites/  comments, ratings, favourites
  search/ main/
```

## Credits

This project is based on the Django online-shop course *دوره آموزشی استادی پایتون در سطح وب* (Python mastery course, web level) by *Mehdi Abbasi*
([course link](https://darsmanco.ir/)). The project structure, the data model and the front-end theme come
from that course. The changes listed in "What differs from the course project" above, including
the payment app, the tests and the configuration, are what I built on top of it.

I used Claude (an AI assistant) to help rewrite the payment app, fix bugs, and write the tests and documentation.
I ran and tested the project myself, including the ZarinPal sandbox payment flow.

## Notes

- `django-ckeditor` bundles CKEditor 4, which is no longer maintained; `django-ckeditor-5` is the
  natural replacement.
- The favicon, the `sprite.svg` icons and the default avatar (`customer/nophoto.jpg`) live in `static/images`.
  Demo images (categories, slides, avatars, products, logos) are in `media/images`; images uploaded
  through the admin (brands, product groups, product galleries, CKEditor) are git-ignored.
- Third-party assets: the front-end theme, fonts and some sample images come from the original course
  project and keep their own licenses. Check them before reusing or redistributing this repository.

## License

Released under the MIT License (see `LICENSE`). The license covers my own code only; third-party
assets (front-end theme, fonts, some sample images) and the original course material keep their own licenses.
