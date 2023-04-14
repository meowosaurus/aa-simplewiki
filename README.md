# SimpleWiki

A simple wiki system for alliance auth. It supports multiple pages with different sections. Every page and every section can have their own icon.

![Showcase](https://i.imgur.com/ALZZ7Bs.png)

### Current Features

* Create custom wiki pages with different sections
* Add an icon next to menus or sections
* Edit pages on the admin panel with HTML
* Basic permission system:
  * Editor permissions can be added to single users or groups via the admin panel
  * Alliance Auth groups are synced to simplewiki: Certain pages can only be seen by a specific group

### ToDo:

* Add repo to pip
* Add dropdown menues
* Add editor interface to create, edit and delete menus and sections
* Add html editor without accessing admin panel
* Extend permission system:
  * Add support for having multiple groups accessing a page 

### Active devs:

* [Meowosaurus](https://github.com/meowosaurus)

## Installation

### Alliance Auth Production

#### Non-Docker Version

1.) Install the pip package via `pip install git+https://github.com/meowosaurus/aa-simplewiki`

2.) Add `simplewiki` to your `INSTALLED_APPS` in your projects `local.py`

3.) Make migrations and migrate, then restart your server

#### Docker Version

1.) Edit your `conf/requirements` and add the following line `git+https://github.com/meowosaurus/aa-simplewiki`

2.) Add `simplewiki` to your `INSTALLED_APPS` in your projects `local.py`

3.) Start your server `docker-compose --env-file=.env up -d`

3.) Run `docker compose exec allianceauth bash`

4.) Run `allianceauth update myauth`

5.) Run `auth migrate`

6.) Run `auth collectstatic`

### Alliance Auth Development 
Make sure you have installed alliance auth in the correct way: https://allianceauth.readthedocs.io/en/latest/development/dev_setup/index.html

1.) Download the repo `git clone https://github.com/meowosaurus/aa-simplewiki`

2.) Make sure it's under the root folder `aa-dev`, not under `myauth` 

3.) Change directory into `aa-dev` aand run `pip install -e aa-simplewiki`

4.) Add `simplewiki` to your `INSTALLED_APPS` in your projects `local.py`

5.) Change directory into `myauth`

6.) Make migrations with `python manage.py makemigrations`

7.) Migrate with `python manage.py migrate`

8.) Restart auth with `python manage.py runserver`

## Usage

1.) Go to `{your_auth_url}/admin` -> SimpleWiki -> Add Menu Item

2.) Give it a title, an index (menu items are sorted by their index from low to high) and a name (the name is the name in the url) and hit save.

3.) Go to `{your_auth_url}/admin` -> SimpleWiki -> Add Page Item

4.) Give it a title, a menu page (this is the menu page it will be under), an index (ordered from low to high) and a content description. This description will be the main content and you can use HTML. Hit save.

5.) Go back to your main auth page, go under Wiki and you've created your first menu and page.

## Permissions
Perm | Admin Site | Auth Site 
 --- | --- | --- 
basic_access | None | Can view all wiki pages
editor | None | Can create, edit and delete wiki pages and menus

## Support
* On Discord: Meowlicious#7045
* Check out our wiki on GitHub: https://github.com/meowosaurus/aa-simplewiki/wiki

