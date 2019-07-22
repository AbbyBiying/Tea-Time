# Import database info
from basic import db, User, Tea
 

###### CREATE ############

# Create all the tables in the database

db.create_all()

# Create new users in the database
sam = User('Sam','sam@gmail.com')
frank = User('Frank','frank@gmail.com')
abby = User('Abby','abbyzhangca@gmail.com')
bibi = User('Bibi','bibireago@163.com')
biying = User('Biying','biyingz.c@gmail.com')

# add these entries to the DB
db.session.add_all([sam,abby,frank,biying,bibi])

# Now save it to the database
db.session.commit()


# # Give some Toys to Rufus
tea1 = Tea('hot','Black',frank.id)
tea2 = Tea("iced",'Green',abby.id)
tea3 = Tea("hot",'Pu-erh',bibi.id)
tea4 = Tea("iced",'Masala_chai',biying.id)
tea5 = Tea("hot",'Oolong',sam.id)

# Commit these changes to the database
db.session.add_all([tea1,tea2,tea3,tea4,tea5])
db.session.commit()

###### READ ##############

# all_users = User.query.all()  
# print(all_users)
# print('\n')

# # Grab by id
# user_two = User.query.get(2)
# print(user_two)
# print('\n')

# # Filters
# user_sam = User.query.filter_by(username="Sam")  
# print(user_sam)
# print('\n')
 
# ###### UPDATE ############

# # Grab the data, then modify it, then save the changes.
# third_user = User.query.get(3)
# third_user.email = 'third@third.com'
# db.session.add(third_user)
# db.session.commit()

# ###### DELETE ############

# delete 1st user
# first_user = User.query.first()
# db.session.delete(first_user)



# Check for changes:

# all_users = User.query.all()   
# all_tea = Tea.query.all()   
# db.session.query(all_users).delete()
# db.session.query(all_tea).delete()

# delete all users and tea
# db.session.query(User).delete()
# db.session.query(Tea).delete()
# db.session.commit()

# abby = User.query.filter_by(username="Abby").first()  
  
# print(all_users)