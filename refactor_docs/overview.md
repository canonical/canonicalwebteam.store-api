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
