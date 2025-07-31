##################################################################
# DOCKERFILE FOR RECIPE-APP-API
#
# This file tells Docker how to build an image for our recipe application API.
# The image contains everything needed to run the application.
#
# Why do we need this?
# - Makes sure the app runs the same way everywhere
# - Packages our code with all required dependencies
# - Simplifies deployment process
##################################################################

# Choose a base image to start from
# We're using a small version of Python that includes Linux tools
FROM python:3.11-alpine3.21

# Add information about who maintains this file
LABEL maintainer="greenDev"

# Make sure Python outputs logs immediately (not delayed)
ENV PYTHONUNBUFFERED=1

# First, copy the list of Python packages we need
# We do this early so Docker can reuse these steps when possible
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Now copy our actual application code into the image
# This is the main functionality of our app
COPY ./app /app

# Set where future commands will run from
# Like changing directories in a file system
WORKDIR /app

# Tell Docker that this container will use port 8000
EXPOSE 8000

# Allow optional installation of development tools
ARG DEV=false

# Install everything our app needs to run:
# 1. Create a special space for Python packages
# 2. Update the package installer
# 3. Add database tools so we can connect to PostgreSQL
# 4. Add temporary tools needed to install some packages
# 5. Install our Python packages from requirements.txt
# 6. If requested, also install development packages
# 7. Clean up temporary files to keep image small
# 8. Create a special user account for security
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    # Install database connection tools
    apk add --update --no-cache postgresql-client jpeg-dev && \
    # Install temporary tools needed for some package installations
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev zlib zlib-dev && \
    # Install our main Python packages
    /py/bin/pip install -r /tmp/requirements.txt && \
    # Only install extra development tools if asked
    if [ "$DEV" = true ]; then \
    /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    # Remove temporary files we don't need anymore
    rm -rf /tmp && \
    # Remove temporary tools we only needed for installation
    apk del .tmp-build-deps && \
    # Create a special user account just for running our app
    adduser \
    --disabled-password \
    --no-create-home \
    django-user && \
    mkdir -p /vol/web/media/uploads && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol/web && \
    chmod -R 775 /vol/web


# Make our Python packages available in the system path
ENV PATH="/py/bin:$PATH"

# Run the container using our special user account instead of root
USER django-user