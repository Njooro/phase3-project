#!/usr/bin/env python3
from db import Base, engine, session
from models import Member, Route, Matatu
from colorama import init, Fore, Style
import click
import re
import csv

init()

@click.group()
def my_commands():
    pass

rd = Fore.RED
bl = Fore.BLUE
gr = Fore.GREEN
mg = Fore.MAGENTA
cyan = Fore.CYAN
yl = Fore.YELLOW
wh = Fore.WHITE

br = Style.BRIGHT
fr = Fore.RESET

smbms= '< SUPER METRO BUS MANAGEMENT SYSTEM >'
print(cyan + br + f'\n{smbms:-^50}\n')


def error(message):
    return f"{rd}{message}{cyan}"

def blue(message):
    return f"{bl}{message}{cyan}\n"

def green(message):
    return f"{gr}{message}{cyan}\n"

def magenta(message):
    return f"{mg}{message}{cyan}\n"

def white(message):
    return f"{wh}{message}{cyan}\n"

def yellow(message):
    return f"{yl}{message}{cyan}\n"


# VALIDATORS

def validate_id(ctx, param, value):
    if not value.isdigit() or len(value) != 8:
        raise click.BadParameter(error('National ID must be 8 digits long.'))
    return value

def validate_phone(ctx, param, value):
    pattern = r'^254[71]\d{8}$'
    
    if not re.match(pattern, value):
        raise click.BadParameter(error("Invalid format. Phone numbers must start with 254."))
    
    return value

def validate_name(ctx, param, value):
    pattern = r'^[A-Za-z\s\.\'-]+ [A-Za-z\s\.\'-]+$'
    if not re.match(pattern, value):
        raise click.BadParameter(error('Invalid format. Enter full name in the correct format.'))
    
    return value

def validate_location(ctx, param, value):
    pattern = r'^[0-9A-Za-z\s\.\'-]+$'
    if not re.match(pattern, value):
        raise click.BadParameter(error('Invalid format.'))
    
    return value

def validate_route(ctx, param, value):
    pattern = r'^[A-Za-z]+-[A-Za-z]+$'
    if not re.match(pattern, value):
        raise click.BadParameter(error('Invalid route. e.g., NRB-Juja'))
    
    return value

def validate_price(ctx, param, value):
    pattern = r'^[1-9][0-9]*[05]$'

    if not re.match(pattern, value):
        raise click.BadParameter(error('Invalid price.'))
    
    return value

def validate_number_plate(ctx, param, value):
    pattern = r'^[K][B-F][A-Z]\s[\d]{3}[A-Z]$'

    if not re.match(pattern, value):
        raise click.BadParameter(error('Invalid plates. e.g., KDF 777A'))
    
    return value


def validate_double_int(ctx, param, value):
    pattern = r'^\d{1,2}$'

    if not re.match(pattern, value) or value == '0':
        raise click.BadParameter(error('Invalid entry.'))
    
    return value

def member_exists(ctx, param, value):
    member = session.query(Member).filter(Member.name == value).first()
    if not member:
        raise click.BadParameter(error('This must be an existing member.'))
    
    return value

def route_exists(ctx, param, value):
    member = session.query(Route).filter(Route.name == value).first()
    if not member:
        raise click.BadParameter(error('This must be an existing route.'))
    
    return value

def member_id_exists(ctx, param, value):
    id = session.query(Member).filter(Member.id == value).first()
    if not id:
        raise click.BadParameter(error('id does not exist. Note that this is not the national id.'))
    
    return value

def route_id_exists(ctx, param, value):
    id = session.query(Route).filter(Route.id == value).first()
    if not id:
        raise click.BadParameter(error('id does not exist.'))
    
    return value 

def matatu_id_exists(ctx, param, value):
    id = session.query(Matatu).filter(Matatu.id == value).first()
    if not id:
        raise click.BadParameter(error('id does not exist.'))
    
    return value


# LOGIC

# Add a new member to the database.
@click.command()
@click.option('--name', prompt='Name', help="Member's full name", callback=validate_name)
@click.option('--national_id', prompt='National ID', help='National ID', callback=validate_id)
@click.option('--location', prompt='Location', help='Location', callback=validate_location)
@click.option('--phone', prompt='Phone', help='Phone number starting with with 254', callback=validate_phone)
def add_member(name, national_id, location, phone):
    """Add a new member to the database."""
    new_member = Member(name=name, national_id=national_id, location=location, phone=phone)

    session.add(new_member)
    session.commit()

    click.echo(f"Added member with ID: {new_member.id}")


# Add a new route to the database.
@click.command()
@click.option('--name', prompt='Name', help="Route name", callback=validate_route)
@click.option('--price', prompt='Price', help="Route price", callback=validate_price)
def add_route(name, price):
    """Add a new route to the database."""
    new_route = Route(name=name, price=price)

    session.add(new_route)
    session.commit()

    click.echo(f"Added member with ID: {new_route.id}")


# Add a new matatu to the fleet.
@click.command()
@click.option('--owner', prompt='Owner Full Name', help='Owner name - must be an existing member', callback=member_exists)
@click.option('--route', prompt='Route Name', help='Route name - must be an existing member', callback=route_exists)
@click.option('--driver-name', prompt='Driver Full Name', help='Driver name', callback=validate_name)
@click.option('--driver-contact', prompt="Driver's Contact", help='Phone number starting with with 254', callback=validate_phone)
@click.option('--number-plate', prompt='Number Plate', help='Matatu number plate', callback=validate_number_plate)
@click.option('--capacity', prompt='Capacity', help='Matatu capacity', callback=validate_double_int)
@click.option('--avg-rounds-pd', prompt='Average Rounds Per Day', help='Average rounds per day', callback=validate_double_int)

def add_matatu(owner, route, driver_name, driver_contact, number_plate, capacity, avg_rounds_pd):
    """Add a new matatu to the fleet. Must be owned by an existing member."""
    new_matatu = Matatu(
        number_plate=number_plate,
        capacity=capacity,
        driver_name=driver_name,
        driver_contact=driver_contact,
        avg_rounds_pd=avg_rounds_pd,
        route_id=session.query(Route).filter(Route.name == route).first().id,
        member_id=session.query(Member).filter(Member.name == owner).first().id,
    )

    session.add(new_matatu)
    session.commit()

    click.echo(f"Added matatu with ID: {new_matatu.id}")

# search members
@click.command()
@click.option('--name', prompt='Name', help='Name of the member to search for')
def find_member_by_name(name):
    """Find a member by name."""
    member = session.query(Member).filter(Member.name == name).first()

    if member:
        click.echo(f"{member}\n")
    else:
        click.echo(error(f"No member found with the name: {name} \n"))

# search routes
@click.command()
@click.option('--name', prompt='Name', help='Name of the route to search for')
def find_route_by_name(name):
    """Find a route by name."""
    route = session.query(Route).filter(Route.name == name).first()

    if route:
        click.echo(f"{route}\n")
    else:
        click.echo(error(f"No route found with the name: {name} \n"))


# search matatus
@click.command()
@click.option('--number_plate', prompt='Number plate', help='Number plate of the matatu to search for')
def find_matatu_by_number_plate(number_plate):
    """Find a matatu by number plate."""
    matatu = session.query(Matatu).filter(Matatu.number_plate == number_plate).first()

    if matatu:
        click.echo(f"{matatu}\n")
    else:
        click.echo(error(f"No matatu found with number plate: {number_plate} \n"))

@click.command()
@click.option('--driver_name', prompt='Driver name', help='Driver name of the matatu to search for')
def find_matatu_by_driver_name(driver_name):
    """Find a matatu by driver name."""
    matatu = session.query(Matatu).filter(Matatu.driver_name == driver_name).first()

    if matatu:
        click.echo(f"{matatu}\n")
    else:
        click.echo(error(f"No matatu found with driver name: {driver_name} \n"))

# delete member 
@click.command()
@click.option('--id', prompt='Member Id', help='Id of the member to delete. This is not the national id.', callback=member_id_exists)
def delete_member(id):
    """Delete a member by id."""

    session.query(Member).filter(Member.id == id).delete()
    session.commit()

    click.echo(green(f"Member deleted successfully! \n"))

# delete route
@click.command()
@click.option('--id', prompt='Route Id', help='Id of the route to delete.', callback=route_id_exists)
def delete_route(id):
    """Delete a route by id."""

    session.query(Route).filter(Route.id == id).delete()
    session.commit()

    click.echo(green(f"Route deleted successfully! \n"))


# delete matatu
@click.command()
@click.option('--id', prompt='Route Id', help='Id of the matatu to delete.', callback=matatu_id_exists)
def delete_matatu(id):
    """Delete a matatu by id."""

    session.query(Matatu).filter(Matatu.id == id).delete()
    session.commit()

    click.echo(green(f"Matatu id {id} deleted successfully! \n"))

# matatu owner
@click.command()
@click.option('--number_plate', prompt='Number plate', help='Number plate of the matatu to search for', callback=validate_number_plate)
def owner_of_matatu(number_plate):
    """Find the owner of a matatu by number plate"""
    matatu = session.query(Matatu).filter(Matatu.number_plate == number_plate).first()

    if matatu:
        id = matatu.member_id
        owner = session.query(Member).filter(Member.id == id).first()
        click.echo(f"{owner}\n")
    else:
        click.echo(error(f"No matatu found with number plate: {number_plate} \n"))


# Generates a CSV file with all matatus plying a certain route

@click.command()
@click.option('--route_id', prompt='Route Id', help='Id of the route to search.', callback=route_id_exists)
@click.option('--filename', prompt='Output Filename', help='Name of the output .csv file.')
def matatus_on_route(route_id, filename):
    """Find all matatus plying this route (.csv)"""
    
    if route_id:
        all_matatus = session.query(Matatu).filter(Matatu.route_id == route_id).all()
                
        if filename.endswith('.csv'):
            file_name = filename
        else:
            file_name = f"{filename}.csv"

        with open(file_name, "w", newline='') as csvfile:
            fieldnames = ['id', 'Driver Name', 'Driver Contact', 'Number Plate', 'Capacity', 'Average Rounds Per Day', 'Owner']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for matatu in all_matatus:
                owner_name_tuple = session.query(Member.name).filter(Member.id == matatu.member_id).first()
                owner_name = owner_name_tuple[0] if owner_name_tuple else ""
                writer.writerow({'id': matatu.id,
                                 'Driver Name': matatu.driver_name,
                                 'Driver Contact': f"+{matatu.driver_contact}",
                                 'Number Plate': matatu.number_plate,
                                 'Capacity': matatu.capacity,
                                 'Average Rounds Per Day': matatu.avg_rounds_pd,
                                 'Owner': owner_name
                                })

        click.echo(green(f"CSV file successfully created as: {file_name}\n"))
    else:
        click.echo(error("Route id not found.\n"))

# All matatus owned by a member
@click.command()
@click.option('--name', prompt='Name', help='Name of the member to search for', callback=member_exists)
def matatus_owned_by(name):
    """All matatus owned by a member."""

    member = session.query(Member).filter(Member.name == name).first()

    if member:
        matatus = session.query(Matatu).filter(Matatu.member_id == member.id).all()

        click.echo(f"{matatus}\n")
    else:
        click.echo(error(f"No matatus found for {name} \n"))


# Generates a CSV file with estimated monthly gross amounts for all matatus

@click.command()
@click.option('--filename', prompt='Output Filename', help='Name of the output .csv file.')
def all_matatu_financials(filename):
    """Est monthly gross amts for all matatus (.csv)"""

    if filename.endswith('.csv'):
        file_name = filename
    else:
        file_name = f"{filename}.csv"

    with open(file_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([
            'Matatu ID', 
            'Number Plate', 
            'Route', 
            'Capacity',
            'Price Per Customer',
            'Avg. Trips Pd', 
            'Owned By', 
            'Gross Amount'
        ])

        matatus = session.query(Matatu).all()

        for matatu in matatus:
            route_price = session.query(Route.price).filter(Route.id == matatu.route_id).first()
            price_per_customer = route_price[0] if route_price else ""
            route_name_tuple = session.query(Route.name).filter(Route.id == matatu.route_id).first()
            route_name = route_name_tuple[0] if route_name_tuple else ""
            owner_name_tuple = session.query(Member.name).filter(Member.id == matatu.member_id).first()
            owner_name = owner_name_tuple[0] if owner_name_tuple else ""
            gross_amount = matatu.capacity * route_price[0] * matatu.avg_rounds_pd * 30
            csv_writer.writerow([
                matatu.id, 
                matatu.number_plate, 
                route_name, 
                matatu.capacity,
                f'{price_per_customer:,}', 
                matatu.avg_rounds_pd, 
                owner_name, 
                f'{gross_amount:,}',
            ])

    click.echo(green(f"CSV file successfully created as: {file_name}\n"))
    


# Add commands to the group
my_commands.add_command(add_member)
my_commands.add_command(add_route)
my_commands.add_command(add_matatu)
my_commands.add_command(find_member_by_name)
my_commands.add_command(find_route_by_name)
my_commands.add_command(find_matatu_by_number_plate)
my_commands.add_command(find_matatu_by_driver_name)
my_commands.add_command(delete_member)
my_commands.add_command(delete_route)
my_commands.add_command(delete_matatu)
my_commands.add_command(owner_of_matatu)
my_commands.add_command(matatus_on_route)
my_commands.add_command(matatus_owned_by)
my_commands.add_command(all_matatu_financials)



if __name__ == '__main__':
    Base.metadata.create_all(engine)
    my_commands()