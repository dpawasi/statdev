Statutory Development
=====================

This project is the Department of Parks and Wildlife Statutory Development
corporate application.

# Environment variables

This project uses **django-confy** to set environment variables (in a `.env` file).
The following variables are required for the project to run:

    DATABASE_URL="postgis://USER:PASSWORD@HOST:5432/DATABASE_NAME"
    SECRET_KEY="ThisIsASecretKey"

Variables below may also need to be defined (context-dependent):

    DEBUG=True
    ALLOWED_DOMAIN=".dpaw.wa.gov.au"
    EMAIL_HOST="email.host"
    EMAIL_PORT=25
    SSO_COOKIE_NAME="oim_dpaw_wa_gov_au_sessionid"
