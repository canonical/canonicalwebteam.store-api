
# Publisher Gateway Documentation

## Table of Contents
- [Introduction](#introduction)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)

## Introduction

The Publisher Gateway is a crucial component of the store API that facilitates communication between the stores and the endpoints exposed at [api.charmhub.io](https://api.charmhub.io/docs). These endpoints were initially grouped based on the stores consuming them which makes it hard to find them and also scale the module. With this refactor, all endpoints hitting the publisher gateway will be in the [publishergw](./publishergw.py) file.

Purpose:
- To make it easy for developers to easily find endpoints hitting publisher gateway.

## Usage

```python
# Example usage
from canonicalwebteam.storeapi.publisher_gateway import PublisherGateway

gateway = PublisherGateway("charms", session)
searched_charms = gateway.find(query, fields)
```

## API Endpoints
These are the available endpoints.
Base URL = `https://api.charmhub.io`

**Note**: name_space refers to a package type, we currently have `charms` for both charms and bundles and `snaps` for snaps.


| Method in publishergw.py | API endpoint | Methods |Docs Link  |
|----------|----------|----------|-------------------|
| find   | /v2/charms/find   | GET     |[find](https://api.snapcraft.io/docs/charms.html#charm_find)|
| get_categories   | /v2/{name_space}/categories     | GET     |  [get categories]()    |
| get_macaroon   | /v1/tokens     | GET     | [get macaroon](https://api.charmhub.io/docs/default.html#get_macaroon)     | 
| issue_macaroon   | /v1/tokens     | POST     | [issue macaroon](https://api.charmhub.io/docs/default.html#issue_macaroon)     | 
| exchange_macaroons   | /v1/tokens/exchange     | POST     | [exchange macaroon](https://api.charmhub.io/docs/default.html#exchange_macaroons)     | 
| exchange_dashboard_macaroons    | /tokens/dashboard/exchange     | POST     | [exchange dashboard macaroon](https://api.charmhub.io/docs/default.html#exchange_dashboard_macaroons)     | 
| macaroon_info   | v1/tokens/whoami     | GET     | [macaroon info](https://api.charmhub.io/docs/default.html#macaroon_info)     | 
| whoami    | v1/whoami     | GET     | [whoami](https://api.charmhub.io/v1/whoami)     | 
|    |      |      |      | 
| get_account_packages  |v1/{package_type}     | GET     |      |
| get_package_metadata   | v1/{name_space}/{package_type}     | GET     | [get package metadata](https://api.charmhub.io/docs/default.html#package_metadata)     |
| update_package_metadata  | /v1/{namespace}/{name}     | PATCH     | [update package metadata](https://api.charmhub.io/docs/default.html#update_package_metadata)     |
| register_package_name   | /v1/{namespace}    | POST     | [register name](https://api.charmhub.io/docs/default.html#register_name) |
| unregister_package_name  | /v1/{namespace}/{name}     | DELETE     | [unregister package name](https://api.charmhub.io/docs/default.html#unregister_package)     |
| get_charm_libraries   |  /v1/{namespace}/libraries/bulk     | POST     | [fetch libraries](https://api.charmhub.io/docs/libraries.html#fetch_libraries)     | 
| get_charm_library   | /v1/{namespace}/libraries/{name}/{library_id}     | GET     | [fetch library](https://api.charmhub.io/docs/libraries.html#fetch_library)    | 
| get_releases   | /v1/{namespace}/{name}/releases     | GET     | [list releases](https://api.charmhub.io/docs/default.html#list_releases)     |
| get_item_details   |  v2/charms/info/{name}     | GET     | [get item details](https://api.snapcraft.io/docs/charms.html#charm_info)     |
| get_collaborators   | v1/{namespace}/{name}/collaborators     | GET     | [get collaborators](https://api.charmhub.io/docs/collaborator.html#get_collaborators)     |
| get_pending_invites   | v1/{namespace}/{name}/collaborators/invites/pending     | GET     | [get pending invites](https://api.charmhub.io/docs/collaborator.html#get_pending_invites)     |
| invite_collaborators   | v1/{namespace}/{name}/collaborators/invites     | POST     | [invite collaborators](https://api.charmhub.io/docs/collaborator.html#invite_collaborators)     |
| revoke_invites   | v1/{namespace}/{name}/collaborators/invites/revoke    | POST     | [Data](https://api.charmhub.io/docs/collaborator.html#revoke_invites)    |
| accept_invite   | v1/{namespace}/{name}/collaborators/invites/accept     | POST     | [Data](https://api.charmhub.io/docs/collaborator.html#accept_invite)     |
| reject_invite   | v1/{namespace}/{name}/collaborators/invites/reject     | POST     | [reject invite](https://api.charmhub.io/docs/collaborator.html#reject_invite)     |
| create_track   | v1/{namespace}/{name}/tracks     | POST     | [create track](https://api.charmhub.io/docs/default.html#create_tracks)     |
| get_store_models  | v1/brand/{brand_account_id}/model     | GET     | [get store models](https://api.charmhub.io/docs/model-service-admin.html#read_models)     |
| create_store_model   | v1/brand/{brand_account_id}/model     | POST     | [create store model](https://api.charmhub.io/docs/model-service-admin.html#create_model)     |
| update_store_model   | v1/brand/{brand_account_id}/model/{model_name}     | PATCH     | [update model](https://api.charmhub.io/docs/model-service-admin.html#update_model)     |
| get_store_model_policies   | v1/brand/{brand_account_id}/model/{model_name}/serial_policy     | GET     | [get model policies](https://api.charmhub.io/docs/model-service-admin.html#read_serial_policies)     |
| create_store_model_policy   | v1/brand/{brand_account_id}/model/{model_name}/serial_policy     | POST     | [Data](https://api.charmhub.io/docs/model-service-admin.html#create_serial_policy)   |
| delete_store_model_policy   | v1/brand/{brand_account_id}/model/{model_name}/serial_policy/{serial_policy_rev}     | DELETE     | [delete model policy](https://api.charmhub.io/docs/model-service-admin.html#delete_serial_policy)     |
| get_store_signing_keys   | v1/brand/{brand_account_id}/signing_key     | GET     | [read signing keys](https://api.charmhub.io/docs/model-service-admin.html#read_signing_keys)     |
| create_store_signing_key   |   v1/brand/{brand_account_id}/signing_key   | POST     | [Data](https://api.charmhub.io/docs/model-service-admin.html#create_signing_key)     |
| delete_store_signing_key   | /v1/brand/{brand_account_id}/signing_key/{signing_key_sha3_384}     | DELETE     | [delete signing key](https://api.charmhub.io/docs/model-service-admin.html#delete_signing_key)     |
| get_brand   | v1/brand/{brand_account_id}     | GET     | [get brand](https://api.charmhub.io/docs/model-service-admin.html#read_brand)     |
| delete_featured_snaps  | /featured     | DELETE     | [delete featured](https://docs.google.com/document/d/1UAybxuZyErh3ayqb4nzL3T4BbvMtnmKKEPu-ixcCj_8)     |
| update_featured_snaps   | /featured     | PUT     | [update featured](https://docs.google.com/document/d/1UAybxuZyErh3ayqb4nzL3T4BbvMtnmKKEPu-ixcCj_8)     | 
