# Device Gateway Refactor Documentation

## Table of Contents
- [Introduction](#introduction)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)

## Introduction

The Device Gateway is a crucial component of the store API that facilitates communication between the stores and the endpoints exposed at [devicegw](https://api.snapcraft.io/docs). These endpoints were initially grouped based on the stores consuming them which makes it hard to find and also scale the module. With this refactor, all endpoints hitting the device gateway will be in the [devicegw](./devicegw.py) file.

Purpose:
- To make it easy for developers to easily find endpoints hitting device gateway.


## Usage

```python
# Example usage
from canonicalwebteam.storeapi.devicegw import DeviceGW

devicegw = DeviceGW(Session(), store="store")

account = devicegw.get_account(flask.session)

```

## API Endpoints
Base URL = `https://api.snapcraft.io/`

These are the available endpoints.

| Method in deviceGW | Endpoint | Methods | Docs Link | Former Location |
|----------|----------|----------|----------|----------|
|     search     |      /api/v1/snaps/search    |    GET      |     https://api.snapcraft.io/docs/search.html#snap_search     |    store.py      |
|     find     |      /v2/snaps/find    |     GET     |     https://api.snapcraft.io/docs/search.html#snaps_find     |     snapstore.py     |
|     get_all_items     |     /api/v1/snaps/search     |     GET     |     https://api.snapcraft.io/docs/search.html#snap_search     |     store.py     |
|     get_category_items     |     /api/v1/snaps/search     |     GET     |     https://api.snapcraft.io/docs/search.html#snap_search     |    store.py      |
|      get_featured_items    |     /api/v1/snaps/search     |     GET     |     https://api.snapcraft.io/docs/search.html#snap_search      |     store.py     |
|     get_publisher_items     |     /api/v1/snaps/search     |   GET       |    https://api.snapcraft.io/docs/search.html#snap_search      |     store.py     |
|     get_item_details     |     api/v2/{name_space}/info/{package_name}     |     GET     |    https://api.snapcraft.io/api/v2/{name_space}/info/{package_name}      |    store.py      |
|     get_public_metrics     |     /api/v1/snaps/metrics     |     POST     |     https://api.snapcraft.io/api/v1/snaps/metrics     |    store.py      |
|     get_categories     |     /api/v2/{name_space}/categories     |     GET     |     https://api.snapcraft.io/api/v2/{name_space}/categories     |     store.py     |
|    get_resource_revisions      |     /v2/charms/resources/{package_name}/{resource_name}/revisions     |     GET     |      https://api.snapcraft.io/docs/charms.html#list_resource_revisions    |    store.py      |
|     get_featured_snaps     |     /api/v1/snaps/search     |     GET     |    https://docs.google.com/document/d/1UAybxuZyErh3ayqb4nzL3T4BbvMtnmKKEPu-ixcCj_8      |     store.py     |