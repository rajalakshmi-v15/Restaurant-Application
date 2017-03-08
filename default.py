def index():
    rests=db(db.auth_user).select(db.auth_user.id,db.auth_user.restaurant_name,db.auth_user.phone_number,db.auth_user.opening_time,db.auth_user.closing_time)
    return locals()

def display_menu():
    rest_id=request.args(0)
    menu_details=db(rest_id==db.restaurant.owner_id).select(db.restaurant.item_name,db.restaurant.price)
    name_rest=db(rest_id==db.auth_user.id).select(db.auth_user.restaurant_name)
    name_of_rest=name_rest.first().restaurant_name
    return locals()

def search():
    form=SQLFORM.factory(Field('timings','time',requires=IS_NOT_EMPTY()))
    if form.process().accepted:
        redirect(URL('search_results',args=form.vars.timings))
    return dict(form=form)

def search_results():
    t=request.args(0)
    results=db((db.auth_user.opening_time <= t) & (db.auth_user.closing_time >= t)).select(db.auth_user.id,db.auth_user.restaurant_name,db.auth_user.phone_number,db.auth_user.opening_time,db.auth_user.closing_time)
    return dict(results=results,t=t)

@auth.requires_login()
def restaurants_owned():
    uid=auth.user_id
    results=db(db.restaurant.owner_id == auth.user_id).select(db.restaurant.owner_id,db.restaurant.item_name,db.restaurant.price)
    form=SQLFORM.factory(Field('item_name'),Field('item_price'))
    if form.process().accepted:
        redirect(URL('add_item',args=[uid,form.vars.item_name,form.vars.item_price]))
    return locals()

@auth.requires_login()
def add_item():
    db.restaurant.insert(owner_id=request.args(0),item_name=request.args(1),price=request.args(2))
    redirect(URL('restaurants_owned'))
    
@auth.requires_login()
def delete_item():
    db((request.args(0) == db.restaurant.owner_id) & (request.args(1) == db.restaurant.item_name)).delete()
    redirect(URL('restaurants_owned'))
    
@auth.requires_login()
def change_price():
    form=SQLFORM.factory(Field('new_price','decimal(5,2)'))
    if form.process().accepted:
        redirect(URL('modify_price',args=[request.args(0),request.args(1),form.vars.new_price]))
    return locals()

@auth.requires_login()
def modify_price():
    db((db.restaurant.owner_id== request.args(0)) & (db.restaurant.item_name==request.args(1))).update(price=request.args(2))
    redirect(URL('restaurants_owned'))

@auth.requires_login()
def confirmation():
    return dict()

@auth.requires_login()
def deregister():
    uid=auth.user_id
    #response.flash('successfully deregistered')
    redirect(URL('logout',args=uid))

@auth.requires_login()
def logout():
    form=auth.logout(next=URL('default','delete_user',args=request.args(0)))
    return dict(form=form)

def delete_user():
    uid=request.args(0)
    db(db.restaurant.owner_id == uid).delete()
    db(db.auth_user.id == uid).delete()
    response.flash = 'you are no longer registered!'
    redirect(URL('index'))

def user():
    auth.settings.login_next=URL('default','restaurants_owned')
    return dict(form=auth())
