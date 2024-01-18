from faker import Faker
import random
from db import session
from models import Member, Route, Matatu


if __name__ == "__main__":

    session.query(Member).delete()
    session.query(Route).delete()
    session.query(Matatu).delete()

    fake = Faker()


    routes = {
        'NRB-Kikuyu': 70,
        'NRB-Juja': 80,
        'NRB-Thika': 100,
        'NRB-Kitengela': 70,
        'NRB-Nong': 60,
        'NRB-Makongeni': 110,
        'NRB-Kahawa': 60,
        'NRB-Rongai': 100,
        'NRB-Kisumu': 1200,
        'NRB-Kakamega': 1100,
    }
    
    all_routes = []
    
    for route_name, route_price in routes.items():
        route = Route(
            name=route_name,
            price=route_price
        )

        session.add(route)
        session.commit()

        all_routes.append(route)


    members = []
    for i in range(60):  # Generate 90 fake members
        member = Member(
            name =fake.name(),
            phone = int(fake.numerify(text='+2547########')), # Generate random, realistic Kenyan phone numbers
            national_id = int(fake.numerify(text=f'{random.randint(1, 4)}#######')), # Generate random, realistic Kenyan ID numbers
            location = random.choice(['Nairobi', 'Thika', 'Mombasa', 'Kisumu', 'Nakuru', 'Juja', 'Machakos'])            
        )

        session.add(member)
        session.commit()

        members.append(member)

    matatus = []
    for route in all_routes:
        for _ in range(random.randint(20, 40)):  # Generate between 0 and 10 matatus per route
            member = random.choice(members)  # Choose a random member in the list
            route = random.choice(all_routes)  # Choose a random route in the list

            sec = random.choice(['B', 'C', 'D'])    
            letter = fake.random_letter().title()
            plates= fake.numerify(text=f'K{sec}{letter} ###{letter}') # Generate random, realistic Kenyan number plates
                
            matatu = Matatu(
                driver_name = fake.name(),
                driver_contact = int(fake.numerify(text='+2547#########')),
                number_plate=plates,
                capacity=random.choice([40, 50]),
                avg_rounds_pd=random.choice([9, 10, 11, 12, 13, 14, 15, 16]),
                member_id=member.id,  # Set the member_id for the matatu
                route_id=route.id,  # Set the route_id for the matatu
            )
            matatus.append(matatu)

    session.bulk_save_objects(matatus)
    session.commit()
    session.close()
    print('Tables seeded successfully!')
