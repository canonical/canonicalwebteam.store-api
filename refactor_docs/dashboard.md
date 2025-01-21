# Dashboard SCA Refactor Documentation

## Table of Contents
- [Introduction](#introduction)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)

## Introduction

The Dashboard Gateway is a crucial component of the store API that facilitates communication between the stores and the endpoints exposed at [SCA](https://dashboard.snapcraft.io/docs). These endpoints were initially grouped based on the stores consuming them which makes it hard to find and also scale the module. With this refactor, all endpoints hitting the dashboard SCA gateway will be in the [dashboard](./dashboard.py) file.

Purpose:
- To make it easy for developers to easily find endpoints hitting dashboard gateway.

**NOTE**
The store team have declared that these gateway will be deprecated and endpoints will be moved to the publisher gateway.

## Usage

```python
# Example usage
from canonicalwebteam.storeapi.dashboard import Dashboard

dashboard = Dashboard(Session())

account = dashboard.get_account(flask.session)

```

## API Endpoints
Base URL = `https://dashboard.snapcraft.io/`

These are the available endpoints.

These endpoints were formerly in different files, the last column of the table below shows the former location of the endpoints

| Method in dashboard.py | Endpoint | Methods | Docs Link |  Former location  |
|----------|----------|----------|----------|---------------|
|       get_macaroon   |      /dev/api/acl    |    POST      |    [get macaroon](https://dashboard.snapcraft.io/docs/reference/v1/macaroon.html)      |    snapstore.py    |
|     whoami     |       /api/v2/tokens/whoami   |     GET     |     [who am I?](https://dashboard.snapcraft.io/docs/reference/v2/en/tokens.html#api-tokens-whoami)     |    snapstore.py    |
|     get_account     |     /dev/api/account     |     GET     |      [get account](https://dashboard.snapcraft.io/docs/reference/v1/account.html#get--dev-api-account)    |    publisher.py    |
|    get_agreement      |    /dev/api/agreement      |     GET     |    [get agreement](https://dashboard.snapcraft.io/docs/reference/v1/snap.html#release-a-snap-build-to-a-channel)      |    publisher.py    |
|     post_agreement     |     /dev/api/agreement     |     POST     |     [post agreement](https://dashboard.snapcraft.io/docs/reference/v1/snap.html#assert-a-build-for-a-snap)    |    publisher.py    |
|    post_register_name      |     /dev/api/register-name/     |      POST    |    [register a snap name](https://dashboard.snapcraft.io/docs/reference/v1/snap.html#register-a-snap-name)      |    publisher.py    |
|     post_register_name_dispute     |    /dev/api/register-name-dispute/      |    POST      |    [register name dispute](https://dashboard.snapcraft.io/docs/reference/v1/snap.html#register-a-snap-name-dispute)      |    publisher.py    |
|     get_snap_info     |    /dev/api/snaps/info/      |    GET      |     [get snap info](https://dashboard.snapcraft.io/docs/reference/v1/snap.html#obtaining-information-about-a-snap)     |     publisher.py     |
|     get_package_upload_macaroon     |     /dev/api/acl/     |     GET     |     [request a macaroon](https://dashboard.snapcraft.io/docs/reference/v1/macaroon.html#request-a-macaroon)     |    publisher.py    |
|      snap_metadata    |     /dev/api/snaps/(snap_id)/metadata     |     PUT     |     [snap metadata](https://dashboard.snapcraft.io/docs/reference/v1/snap.html#managing-snap-metadata)     |    publisher.py    |
|     snap_screenshots     |     /dev/api/snaps/(snap_id)/metadata     |     PUT     |    [snap screenshots](https://dashboard.snapcraft.io/docs/reference/v1/snap.html#managing-snap-metadata)      |    publisher.py    |
|     get_snap_revision     |     /dev/api/acl/     |     GET     |    [get snap revision]()      |    publisher.py    |
|     snap_release_history     |     /api/v2/snaps/(?P<name>[\\w-]+)/releases   |    GET    |     [snap release history](https://dashboard.snapcraft.io/docs/reference/v2/en/snaps.html#snap-releases)     |    publisher.py    |
|    snap_channel_map      |    /api/v2/snaps/(?P<name>[\\w-]+)/channel-map      |     GET     |    [snap channel map](https://dashboard.snapcraft.io/docs/reference/v2/en/snaps.html#snap-channel-map)      |    publisher.py    |
|    post_snap_release      |    /dev/api/snap-release/      |    POST      |    [post snap release](https://dashboard.snapcraft.io/docs/reference/v1/snap.html#release-a-snap-build-to-a-channel)      |    publisher.py    |
|     post_close_channel     |     /dev/api/snaps/{snap_id}/close     |     POST     |    [post close channel](https://dashboard.snapcraft.io/docs/reference/v1/snap.html#close-a-channel-for-a-snap-package)      |    publisher.py    |
|     get_publisher_metrics     |    /dev/api/snaps/metrics      |      POST    |     [get publisher metrics](https://dashboard.snapcraft.io/docs/reference/v1/snap.html#fetch-metrics-for-snaps)     |    publisher.py    |
|    get_validation_sets      |     /api/v2/validation-sets     |     GET     |    [get validation sets](https://dashboard.snapcraft.io/docs/reference/v2/en/validation-sets.html)      |    snapstore.py    |
|     get_validation_set     |     /api/v2/validation-sets/{id}     |     GET     |     [get validation set](https://dashboard.snapcraft.io/docs/reference/v2/en/validation-sets.html)     |    snapstore.py    |
|    get_stores      |     /dev/api/account     |    GET      |     [get stores](https://dashboard.snapcraft.io/docs/reference/v1/account.html#get--dev-api-account)     |    snapstore.py    |
|    get_store      |     /api/v2/stores/{store_id}     |     GET     |     [get store](https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#list-the-details-of-a-brand-store)     |    snapstore.py    |
|     get_store_snaps     |     /api/v2/stores/{store_id}/snaps     |    GET      |     [get store snaps](https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#get)     |    snapstore.py    |
|     get_store_members     |     /api/v2/stores/{store_id}     |     GET     |     [get store members](https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#list-the-details-of-a-brand-store)     |    snapstore.py    |
|     update_store_members     |     /api/v2/stores/{store_id}/users     |     POST     |     [update store members](https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#add-remove-or-edit-users-roles)     |    snapstore.py    |
|     invite_store_members     |     /api/v2/stores/{store_id}/invites     |    POST     |     [invite store members](https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#manage-store-invitations)     |    snapstore.py    |
|     change_store_settings     |    /api/v2/stores/{store_id}/settings      |    PUT      |     [change store settings](https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#change-store-settings)     |    snapstore.py    |
|     update_store_snaps     |    api/v2/stores/{store_id}/snaps      |    POST      |    [update store snaps](https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#post)      |    snapstore.py    |
|     update_store_invites     |    /api/v2/stores/{store_id}/invites      |    PUT      |    [update store invites](https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#manage-store-invitations)     |    snapstore.py    |
|    get_store_invites      |    /api/v2/stores/{store_id}      |     GET     |     [get store invites](https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#list-the-details-of-a-brand-store)     |    snapstore.py    |
