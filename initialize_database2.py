from faker import Faker
from datetime import datetime, timedelta


from config import Session
from models import Sales, User, Work

if __name__ == "__main__":
    session = Session()
    fake = Faker()

    # insert employees
    for _ in range(10):
        username = fake.user_name()
        password = fake.password()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email_address = fake.email()
        is_admin = fake.boolean(chance_of_getting_true=20)  # 20% chance of being an admin
        is_working = fake.boolean(chance_of_getting_true=80)  # 80% chance of being "working"

        # Create a User instance with the generated data
        user = User(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email_address=email_address,
            is_admin=is_admin,
            is_working=is_working
        )

        # Add the user instance to the session
        session.add(user)

    session.commit()

    # Get all user IDs from the User table
    user_ids = [user.id for user in session.query(User).all()]

    # Generate and insert random sales and work data
    for _ in range(10):  # Generate data for 10 records (adjust as needed)
        # Random user ID for sales and work
        user_id = fake.random_element(elements=user_ids)

        # Random amount for sales
        amount = fake.random_int(min=100, max=10000)

        # Random start and end datetimes for sales and work
        start_datetime = fake.date_time_between(start_date="-1y", end_date="now", tzinfo=None)
        end_datetime = start_datetime + timedelta(hours=fake.random_int(min=1, max=48))

        # Create Sales and Work instances
        sales = Sales(manager_id=user_id, amount=amount, start_datetime=start_datetime, end_datetime=end_datetime)
        work = Work(user_id=user_id, start_datetime=start_datetime, end_datetime=end_datetime)

        # Add to session
        session.add(sales)
        session.add(work)

    # insert sales

    session.commit()
    session.close()