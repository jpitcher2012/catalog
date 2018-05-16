from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Breed, Group, User

engine = create_engine('sqlite:///dogbreeds.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Hound Group
group1 = Group(
    id=1,
    name="Hound",
    description="""Originally classified as sporting dogs because of their
        function as hunters, breeds in the Hound Group are of a great variety
        of size, shape and coat. Most of these breeds were developed to hunt
        somewhat independently for their humans, who usually followed on foot
        or on horseback as the hounds chased down the prey. This group
        informally consists of scent hounds, dogs that hunt by tracking a
        scent, and sight hounds, who spot their game and run it down.""",
    picture="group1.jpg")
session.add(group1)
session.commit()

# Terrier Group
group2 = Group(
    id=2,
    name="Terrier",
    description="""All but two of the terriers evolved in the British Isles.
        The geography of the specific area (water, rocky terrain) helped to
        determine the exact duties of each breed, but it usually involved
        hunting vermin and varmints ranging from rats to badgers to otters and
        more. These are dogs of great determination, courage and
        self-confidence, with a great willingness to go to ground in search of
        its quarry.""",
    picture="group2.jpg")
session.add(group2)
session.commit()

# Working Group
group3 = Group(
    id=3,
    name="Working",
    description="""While the uses and appearances of the dogs in the Working
        Group vary, most are powerfully built and intelligent, performing
        various tasks for their people. These dogs are working farm and draft
        animals. They guard homes and livestock, serve heroically as police and
        military dogs, security dogs, guide and service dogs and hunters.""",
    picture="group3.jpg")
session.add(group3)
session.commit()

# Herding Group
group4 = Group(
    id=4,
    name="Herding",
    description="""Herding is a natural instinct in dogs that is seen in the
        wild. Humans have used that instinct to their advantage on farms and
        ranches with herding dogs who have the sole purpose of gathering and
        moving livestock from one place to another.""",
    picture="group4.jpg")
session.add(group4)
session.commit()

# Sporting Group
group5 = Group(
    id=5,
    name="Sporting",
    description="""The invention of the gun led to the development of the
        sporting, or gun dogs, to aid in hunting upland game birds or
        waterfowl, performing at the direction of the hunter.While a number of
        these breeds perform more than one task, it is generally the duty of
        pointers and setters to point and mark game; for spaniels to flush
        game; and for retrievers to recover dead and wounded game.""",
    picture="group5.jpg")
session.add(group5)
session.commit()

# Non-Sporting Group
group6 = Group(
    id=6,
    name="Non-Sporting",
    description="""The AKC originally registered dogs as either Sporting or
        Non-Sporting. Eventually, hounds and terriers were split from the
        Sporting Group, and the Toys and Working dogs were split off from
        Non-Sporting, with the Herding Group eventually splitting from Working.
        Today, the Non-Sporting Group is literally every breed that is left,
        resulting in a wide variety of sizes, shapes, hair, function and
        history.""",
    picture="group6.jpg")
session.add(group6)
session.commit()

# Toy Group
group7 = Group(
    id=7,
    name="Toy",
    description="""Toy dogs have been around for centuries, and are bred for
        one purpose: to be companions for their humans. Many have been bred
        down from and still resemble their larger cousins.Their small size and
        portability make them ideal for city dwellers and those with limited
        space.""",
    picture="group7.jpg")
session.add(group7)
session.commit()
