# MCQ-Quiz Exam Web App

### Demo

[Link](https://tf-quiz.herokuapp.com/)

#### Initially developed for [Technofest 2020](https://technofest-2020.herokuapp.com/), Organized by COMeIT - Government Polytechnic, Pune

## Features

-   Question Randomization

-   Two-way Question Sync

    > Submitted Questions & Answers are synced on both Server & Client with persistance across Page Refreshes.

-   Multiple Quiz Subjects Support:

    > Add as many as Subjects from the script.

    > Questions per User & Time limit can be configured for Each Subject individually.

-   Time Synchronization

    > Time left is synchronized. Page Refreshes won't reset the timmer.

-   Leaderboard

    > Realtime Score updates for each event

-   Automatic Question Insertion from .xlsx

## Setup

Configure following Environment Variables in a .env file :

```
SECRET_KEY
DATABASE_URI
```

Create Database :

```
python manage.py create_db
```

Add Events :

```
python manage.py add_events
```

Add Questions from .xlsx:

> Create .xlsx file for Questions from Format Provided in the [`Questions`](/Questions) Directory.

```
python manage.py excel_to_db
```

Setup Admin:

```
python manage.py setup_admin

```

#### License

MIT
