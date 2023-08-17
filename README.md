# Instagram clone 


## Problem Statement
- To build a app similar to instagram with basic features like posting images, liking, commenting, following, unfollowing, searching, etc.

## Tech Stack
- Frontend: Flutter, Dart
- Backend: Django, Python, Django Rest Framework
- Database: PostgreSQL
- Build Tools: Docker, Docker Compose


## Features
- User can create an account.
- OTP will be used to verify the user.
- User can login using email and password.
- User can post images with caption and location
- User can update the post.
- User can delete the post.
- User can like, comment, save the post.
- User can follow and unfollow other users.
- User can search for other users.
- User can edit their profile by changing their profile picture, username, bio, etc.
- User can see their own profile and other users profile and followers and following.
- User can see their own posts and posts of other users.
- User can see the posts of the users they follow in the feed.

## Upcoming Features
- User can send and receive messages in real time.
- User can see the stories of the users they follow.
- User can see the posts of the users they follow in the feed in real time.
- User can also post videos.
- User can also post multiple images in a single post.
- User can tag other users in their posts, comments and captions.
- User can also share posts.
- User can also save posts in collections.
- and many more...


## How to run the project
- Clone the repository of both frontend and backend.
- Make sure that you have `docker` and `docker-compose` installed on your system.
- Go to the backend directory and in docker folder
- Run `docker-compose up -d` in the backend directory.
- The backend will start running on `http://localhost/`.
- Go to the frontend directory
- Run `flutter pub get` in the frontend directory.
- Modify the value of `url` in `lib/data.dart` to `http://localhost/`.
- Run `flutter run` in the frontend directory.
- The frontend will start running on the emulator or the device connected to your system.


## Hope you liked the project and find it useful.

