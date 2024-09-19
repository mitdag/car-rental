```mermaid
erDiagram
    User ||--o{ Car : owns
    User ||--o{ Rental : rents
    User {
        int user_id PK
        string name
        string email
        string password
        string phone_number
        string user_type
        float rating
        boolean is_verified
    }
    Car ||--o{ Rental : "is rented in"
    Car ||--o{ Favorite : "is favorited in"
    Car {
        int car_id PK
        int owner_id FK
        string make
        string model
        int year
        string car_type
        float price_per_day
        string location
        text description
        text rules
    }
    Rental {
        int rental_id PK
        int car_id FK
        int renter_id FK
        date start_date
        date end_date
        float total_price
        string status
    }
    Payment {
        int payment_id PK
        int rental_id FK
        float amount
        string payment_method
        datetime payment_date
        string status
    }
    Review {
        int review_id PK
        int rental_id FK
        int reviewer_id FK
        int reviewee_id FK
        int rating
        text comment
        datetime review_date
    }
    Favorite {
        int favorite_id PK
        int user_id FK
        int car_id FK
    }
    Notification {
        int notification_id PK
        int user_id FK
        string type
        text message
        datetime created_at
        boolean is_read
    }
    Dispute {
        int dispute_id PK
        int rental_id FK
        int reporter_id FK
        text description
        string status
        datetime created_at
    }
    Rental ||--|| Payment : has
    Rental ||--o{ Review : receives
    User ||--o{ Favorite : has
    User ||--o{ Notification : receives
    Rental ||--o{ Dispute : may_have
```
