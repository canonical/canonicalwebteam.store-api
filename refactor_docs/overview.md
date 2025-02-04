# Project Overview

## Introduction
This is a detailed documentation for refactoring the store-api module.

## Goals
- To refactor the store-API module
- To structure the store-API module based on the store team's authentication gateways
- To ensure all endpoints are grouped based on the authentication gateways

## Motivation
Of the various importance of modules, code organization and reusability can not be overemphasized. The store-API module is presently fulfilling the purpose of reusablity as it serves as a proxy between both charmhub.io and snapcraft.io and the store team's exposed API endpoints. However, the module is not meeting upto the standard for a properly organized code structure. This makes it a bit challenging to find methods, it becomes a thing of great concern as more stores are emerging which would lead to the module growing in complexity making it harder to scale and maintain.

Therefore, there is need to refactor and restructure the codebase in such a way that allows for easy usage, scability and easy maintainance.

## Scope
The scope of the project is to:
- Move all endpoints hitting the api.charmhub.io to `publishergw.py`
- Move all endpoints hitting the dashboard.snapcraft.io to `dashboard.py`
- Move all endpoints hitting api.snapcraft.io to `devicegw.py`
- Refactor Charmhub and snapcraft to use the refcatored module
- Document all changes made

## How methods are reorganized
In the past, we had the `Publisher` and `Store` classes that were inherited by `CharmPublisher`, `SnapPublisher` and `CharmStore`, `SnapStore` respectively. These groupings were based on the store frontends (Charmhub and Snapcraft). Endpoints related to publisher features in `Charmhub` and `Snapcraft` were found in `CharmPublisher`  and `SnapPublisher` respectively, while endpoints related to stores in `Charmhub` and `Snapcraft` were found in `CharmStore` and `SnapStore` respectively. These classes (`CharmPublisher`, `CharmStore`, `SnapPublisher`, `SnapStore`) all consume API endpoints from one or more of the three available API gateways which are [publisher-gateway](https://api.charmhub.io), [dashboard-SCA](https://dashboard.snapcraft.io), [device-gateway](https://api.snapcraft.io).

With this refactor, methods are regrouped based on these API gateways, we now have a `Base` class for methods that are common to all and we have `Dashboard`, `Publishergw` and `Devicegw` classes inheriting from the `Base` class and having all methods related to them. The implication of this is that, for example in `Dashboard`, only methods that are consuming SCA endpoints will be found, same goes for `Publisher` and `Device`. Example usage in store frontends can be found in the specific gateway documentation [dashboard](./dashboard.md), [devicegw](./devicegw.md) and [publishergw](./publishergw.md).


### Deprecated methods
- whoami: this method has been taken out of the repo as it has been deprecated by the store team and it is not used by any of the stores.