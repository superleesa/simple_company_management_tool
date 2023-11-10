from faker import Faker
from datetime import datetime, timedelta


from config import Session
from models import Project, User, Work, Client

if __name__ == "__main__":
    session = Session()
    fake = Faker()

    # ===========PARAMS===========
    num_employees= 10
    num_work_sessions = 150
    num_clients = 5
    num_projects = 15

    # insert employees
    for _ in range(num_employees):
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


    # generate and insert clients
    for i in range(num_clients):
        client_name = "Company" + str(i)
        client = Client(name=client_name)
        session.add(client)

    session.commit()

    client_ids = [client.id for client in session.query(Client).all()]


    # generate and insert project records
    # Create Sales and Work instances
    for _ in range(num_projects):
        # select a random client and manager
        manager_id = fake.random_element(elements=user_ids)
        client_id = fake.random_element(elements=client_ids)

        # Random amount for sales
        amount = fake.random_int(min=100, max=10000)
        start_datetime = fake.date_time_between(start_date="-1y", end_date="now", tzinfo=None)
        end_datetime = start_datetime + timedelta(days=fake.random_int(min=15, max=365))

        project = Project(client_id=client_id, manager_id=manager_id, earnings=amount, start_date=start_datetime.date(), received_earning_datetime=end_datetime)


    # generate and insert work records
    for _ in range(num_work_sessions):
        # Random user ID for sales and work
        user_id = fake.random_element(elements=user_ids)

        # Random start and end datetimes for sales and work
        start_datetime = fake.date_time_between(start_date="-1y", end_date="now", tzinfo=None)
        end_datetime = start_datetime + timedelta(hours=fake.random_int(min=1, max=48))
        worked_hours = (end_datetime - start_datetime).seconds // 3600 if end_datetime is not None else None

        work = Work(user_id=user_id, start_datetime=start_datetime, end_datetime=end_datetime, worked_hours=worked_hours)

        # Add to session
        session.add(work)

    # insert sales

    session.commit()
    session.close()
