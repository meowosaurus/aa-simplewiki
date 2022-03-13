# Example plugin app for Alliance Auth (GitHub Version)

This is an example plugin app for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth)
(AA) that can be used as starting point to develop custom plugins.

![License](https://img.shields.io/badge/license-GPLv3-green)
![python](https://img.shields.io/badge/python-3.8-informational)
![django](https://img.shields.io/badge/django-3.2-informational)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)

_(These badges are examples, you can and should replace them with your own)_

For the GitLab version of this example app, please have a look over here, Erik
Kalkoken was so friendly to provide it » [Alliance Auth Example App (GitLab Version)](https://gitlab.com/ErikKalkoken/allianceauth-example-plugin)


## Features

- The plugin can be installed, upgraded (and removed) into an existing AA
  installation using PyInstaller.
- It has its own menu item in the sidebar.
- It has one view that shows a panel and some text


## How to use it

To use this example as basis for your own development just fork this repo and then
clone it on your dev machine.

You then should rename the app, and then you can install it into your AA dev
installation.


### Cloning from repo

For this app we are assuming that you have all your AA projects, your virtual
environment and your AA installation under one top folder (e.g. aa-dev).

This should look something like this:

```text
aa-dev
|- venv/
|- myauth/
|- aa-example-plugin
|- (other AA projects ...)
```

Then just cd into the top folder (e.g. aa-dev) and clone the repo from your fork.
You can give the repo a new name right away (e.g. `aa-your-app-name`). You also want
to create a new git repo for it.
Finally, enable [pre-commit](https://pre-commit.com) to enable automatic code style
checking.

```bash
git clone https://github.com/YourName/aa-example-plugin.git aa-your-app-name
cd aa-your-app-name
rm -rf .git
git init
pre-commit install
```

### Renaming the app

Before installing this app into your dev AA you need to rename it to something
suitable for your development project. Otherwise, you risk not being able to install
additional apps that might also be called example.

Here is an overview of the places that you need to edit to adopt the name.

Easiest is to just find & replace `example` with your new app name in all files
listed below.

One small warning about picking names: Python is a bit particular about what special
characters are allowed for names of modules and packages. To avoid any pitfalls I
would therefore recommend to use only normal characters (a-z) in your app's name
unless you know exactly what you are doing.

| Location                                 | Description                                                                            |
|------------------------------------------|----------------------------------------------------------------------------------------|
| `./example/`                             | Folder name                                                                            |
| `./example/templates/example/`           | Folder name                                                                            |
| `./setup.cfg`                            | Update module name for version import, update package name, update title, author, etc. |
| `./example/apps.py`                      | App name                                                                               |
| `./example/__init__.py`                  | App name                                                                               |
| `./example/auth_hooks.py`                | Menu hook config incl. icon and label of your app's menu item appearing in the sidebar |
| `./example/models.py`                    | App name                                                                               |
| `./example/urls.py`                      | App name                                                                               |
| `./example/views.py`                     | Permission name and template path                                                      |
| `./example/templates/example/base.html`  | Title of your app to be shown in all views and as title in the browser tab             |
| `./example/templates/example/index.html` | Template path                                                                          |
| `./testauth/settings.py`                 | App name                                                                               |
| `./.coveragerc`                          | App name                                                                               |
| `./README.md`                            | Clear content                                                                          |
| `./LICENSE`                              | Replace with your own license                                                          |
| `./tox.ini`                              | App name                                                                               |
| `./.isort.cfg`                           | App name for `import_heading_firstparty`                                               |
| `./Makefile`                             | App name and package name                                                              |


## Clearing migrations

Instead of renaming your app in the migrations it's easier to just recreate them
later in the process. For this to work you need to delete the old migration files in
your `migrations` folder.

```bash
rm your-app-name/migrations/0001_initial.py
rm -rf your-app-name/migrations/_pycache
```


## Installing into your dev AA

Once you have cloned or copied all files into place and finished renaming the app
you are ready to install it to your dev AA instance.

Make sure you are in your venv. Then install it with pip in editable mode:

```bash
pip install -e aa-your-app-name
```

First add your app to the Django project by adding the name of your app to
INSTALLED_APPS in `settings/local.py`.

Next we will create new migrations for your app:

```bash
python manage.py makemigrations
```

Then run a check to see if everything is set up correctly.

```bash
python manage.py check
```

In case they are errors make sure to fix them before proceeding.

Next perform migrations to add your model to the database:

```bash
python manage.py migrate
```

Finally, restart your AA server and that's it.


## Installing into production AA

To install your plugin into a production AA run this command within the virtual
Python environment of your AA installation:

```bash
pip install git+https://github.com/YourName/aa-your-app-name
```

Alternatively you can create a package file and manually upload it to your
production AA:

```bash
pip install build
python -m build
```

You'll find the package under `./dist/aa-your-app-name.tar.gz` after this.

Install your package directly from the package file:

```bash
pip install aa-your-app-name.tar.gz
```

Then add your app to `INSTALLED_APPS` in `settings/local.py`, run migrations and
restart your allianceserver.


## Contribute

If you made a new app for AA please consider sharing it with the rest of the
community. For any questions on how to share your app please contact the AA devs on
their Discord. You find the current community creations
[here](https://gitlab.com/allianceauth/community-creations).
