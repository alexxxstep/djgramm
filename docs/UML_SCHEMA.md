# djgramm Database Schema

## ER Diagram (Mermaid)

```mermaid
classDiagram
    class User {
        +Integer id
        +String email
        +String username
        +String first_name
        +String last_name
        +Boolean is_staff
        +Boolean is_active
        +Boolean is_email_verified
        +DateTime date_joined
        +get_full_name()
    }

    class Profile {
        +Integer id
        +Integer user_id
        +Text bio
        +ImageField avatar
        +DateTime created_at
        +DateTime updated_at
        +get_avatar_url()
    }

    class Post {
        +Integer id
        +Integer author_id
        +Text caption
        +DateTime created_at
        +DateTime updated_at
        +get_likes_count()
        +is_liked_by(user)
    }

    class PostImage {
        +Integer id
        +Integer post_id
        +ImageField image
        +Integer order
        +DateTime created_at
    }

    class Tag {
        +Integer id
        +String name
        +SlugField slug
        +DateTime created_at
        +save()
    }

    class Like {
        +Integer id
        +Integer user_id
        +Integer post_id
        +DateTime created_at
    }

    User "1" -- "1" Profile : has
    User "1" -- "*" Post : authors
    Post "1" *-- "*" PostImage : contains
    Post "*" -- "*" Tag : tagged with
    User "*" -- "*" Post : likes
    User "1" -- "*" Like : creates
    Post "1" -- "*" Like : has
```

## Опис Моделей та Логіки

### 1. User (AbstractUser)

Розширена стандартна модель користувача Django.

- **email**: Основний ідентифікатор (унікальний). Використовує стандартні `Django Validators` для перевірки формату.
- **first_name**, **last_name**: Ім'я та прізвище.
- **is_email_verified**: Прапорець підтвердження пошти.
- _(Верифікація реалізується через View та Django `default_token_generator`, без додаткових методів у моделі)_

### 2. Profile

Додаткова інформація про користувача.

- **user**: Зв'язок One-to-One з User.
- **bio**: Короткий опис про себе.
- **avatar**: Фото профілю.
  _(Поле `full_name` прибрано, щоб уникнути дублювання з User)_

### 3. Post

Основна одиниця контенту.

- **author**: Зв'язок ForeignKey з User.
- **caption**: Текстовий опис.
- **tags**: Зв'язок Many-to-Many з Tag.

### 4. PostImage

Зображення для поста (підтримка галереї).

- **post**: Зв'язок ForeignKey з Post.
- **image**: Файл зображення.
- **order**: Порядок відображення в каруселі.

### 5. Interactions (Like)

- **Like**: Проміжна таблиця для зв'язку User-Post (хто лайкнув що).
  - Унікальність пари `[user, post]` (не можна лайкнути двічі).
