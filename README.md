# SimpleWiki
A simple wiki plugin for alliance auth. It supports multiple pages with different sections. Every page and every section can have their own icon. Written in Python with Django.

# Contents
* [Current Features](#current-features)
  * [TODO](#todo)
  * [Planned](#planned)
* [Screenshots](#screenshots)
* [Installation](#installation)
  * [Alliance Auth Production](#alliance-auth-production)
    * [Non-Docker Version](#non-docker-version)
    * [Docker Version](#docker-version)
  * [Alliance Auth Development](#alliance-auth-development)
* [Usage](#usage)
* [Permissions](#permissions)
* [Support](#support)

# Current Features
* Create custom wiki menus with dropdowns plus different sections on each menu
* Add an icon next to menus or sections
* Edit pages on the admin panel with [markdown](https://www.markdownguide.org/cheat-sheet/)
  * Support for all major GitHub markdown features
  * Support for videos (YouTube and Vimeo)
  * Support for alerts and Google Drive
* Search function: Search across all wiki menus and sections
* Permission system:
  * Editor permissions can be added to single users or groups via the admin panel
  * Alliance Auth groups are synced to simplewiki: Certain pages can only be seen by a specific group
  * Multiple groups support: As long as the user is in any of the required groups, they can access the menu
* Editor interface
  * Users with editor permission can create, edit and delete custom menus and sections (editor_access)
  * Users with editor permission see edit and delete buttons above all sections (editor_access)
  * Change menu position's with a drag and drop system

## TODO:
* Quality-of-life updates
* Implement better logging
* Improve code documentation
* Markdown
  * Buttons

## Planned
* Add translations for 
  * German
  * Spanish
  * Chinese
  * Russian
  * Korean 
  * French
  * Italian

### Active devs:
* [Meowosaurus](https://github.com/meowosaurus)

## Screenshots
![Showcase](https://i.postimg.cc/BQc3hPYb/vmplayer-Kvz8-DNZa-M0.gif)

### Search
![Search](https://i.imgur.com/wW69LFN.png)

### Admin Panel
![Menu Admin](https://github.com/meowosaurus/aa-simplewiki/blob/master/images/menu_admin_panel.png)

![Menu Edit](https://github.com/meowosaurus/aa-simplewiki/blob/master/images/menu_admin_panel_edit.png)

![Menu Sorting](https://github.com/meowosaurus/aa-simplewiki/blob/master/images/menu_sorting.gif)

![Section Edit](https://i.imgur.com/3LrysW7.png)

## Installation

### Alliance Auth Production

#### Non-Docker Version
1.) Install the pip package via `pip install aa-simplewiki`

2.) Add `simplewiki` to your `INSTALLED_APPS` in your projects `local.py`

3.) Restart your server, then run migrations and collectstatic

#### Docker Version
1.) Please make sure you followed the custom docker-image tutorial [here](https://gitlab.com/allianceauth/allianceauth/-/tree/master/docker#using-a-custom-docker-image): 

2.) Edit your `conf/requirements` and add the following line `aa-simplewiki` (Check https://pypi.org/project/aa-simplewiki/ for different versions!)

3.) Add `simplewiki` to your `INSTALLED_APPS` in your projects `local.py`

4.) Start your server `docker compose --env-file=.env up -d`

5.) Run `docker compose exec allianceauth bash`

7.) Run `auth migrate`

8.) Run `auth collectstatic`

### Alliance Auth Development 
Make sure you have installed alliance auth in the correct way: https://allianceauth.readthedocs.io/en/latest/development/dev_setup/index.html

1.) Download the repo `git clone https://github.com/meowosaurus/aa-simplewiki`

2.) Make sure it's under the root folder `aa-dev`, not under `myauth` 

3.) Change directory into `aa-dev` aand run `pip install -e aa-simplewiki`

**Important**: If you are getting an error saying that `simplewiki` is not installed after running `pip install -e aa-simplewiki`, delete the `setup.py` file in the aa-simplewiki root directory and try again.

4.) Add `simplewiki` to your `INSTALLED_APPS` in your projects `local.py`

5.) Change directory into `myauth`

6.) Make migrations with `python manage.py makemigrations`

7.) Migrate with `python manage.py migrate`

8.) Restart auth with `python manage.py runserver`

## Usage
Check out our wiki on GitHub: https://github.com/meowosaurus/aa-simplewiki/wiki

1.) Go to `{your_auth_url}/admin` -> SimpleWiki -> Add Menu Item

2.) Give it a title, an index (menu items are sorted by their index from low to high) and a name (the name is the name in the url) and hit save.

3.) Go to `{your_auth_url}/admin` -> SimpleWiki -> Add Page Item

4.) Give it a title, a menu page (this is the menu page it will be under), an index (ordered from low to high) and a content description. This description will be the main content and you can use HTML. Hit save.

5.) Go back to your main auth page, go under Wiki and you've created your first menu and page.

## Permissions
Perm | Admin Site | Auth Site 
 --- | --- | --- 
basic_access | None | Can view all wiki pages
editor_access | None | Can create, edit and delete wiki pages and menus

## Commands
- Migrate all data from 1.0.x to 1.1.x: `python manage.py simplewiki_migrate_v1_1`

## Dependencies
- [Alliance Auth](https://gitlab.com/allianceauth/allianceauth)
- [allianceauth-app-utils](https://gitlab.com/ErikKalkoken/allianceauth-app-utils)
- [Mistune](https://github.com/lepture/mistune)
- [jQuery](https://github.com/jquery/jquery)
- [Nestable](https://github.com/dbushell/Nestable)

## Support
* On Discord: meowlicious
