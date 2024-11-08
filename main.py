from fastapi import FastAPI, HTTPException, Query, Path, Header, Cookie, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from typing import Annotated
from fastapi.responses import JSONResponse


app = FastAPI(title="Картины на заказ",
    description="Посетители создают заказ, художники его выполняют")

@app.get("/")
async def read_root():
    return {"Hello": "World"}
   

class Voucher(BaseModel):
    id: int = Field(..., example=10)
    login: str = Field(..., example="198login")
    amount_pictures: int = Field(..., example=3)
    price: int = Field(..., example=100)
    description: str = Field(..., example="3 pictures for 100$")
    status: Literal['placed', 'in work', 'ready'] = Field(..., example='placed')
    style: Literal[
        'realism', 'impressionism', 'fauvism', 'modern',
        'expressionism', 'cubism', 'futurism', 'abstractionism',
        'dadaism', 'pop-art'
    ] = Field(..., example='realism')


class Account(BaseModel):
    login: str = Field(..., example='10')
    password: str = Field(..., example='theAccounts')
    surName: str = Field(..., example='Green')
    firstName: str = Field(..., example='John')
    patronymic: Optional[str] = Field(None, example='James')
    email: str = Field(..., example='john@email.com')
    type_role: str = Field(..., example='artist')
    phone: str = Field(..., example='12345')
    sex: Literal['f', 'm'] = Field(..., example='m')
    date_of_birth: str = Field(..., example='2000-01-01')  # формат даты


class Visitor(BaseModel):
    login: str = Field(..., example='10')
    id: int = Field(..., example=10)
    residence: str = Field(..., example='Yaroslavl, st/ Syrkova')


class Artist(BaseModel):
    login: str = Field(..., example='10')
    id: int = Field(..., example=10)
    style: Literal[
        'realism', 'impressionism', 'fauvism', 'modern',
        'expressionism', 'cubism', 'futurism', 'abstractionism',
        'dadaism', 'pop-art'
    ] = Field(..., example='realism')


# Пример базы данных
artists_db = [
    Artist(login='artist1', id=1, style='realism'),
    Artist(login='artist2', id=2, style='impressionism'),
    Artist(login='artist3', id=3, style='modern'),
    Artist(login='artist2', id=4, style='impressionism'),
    Artist(login='artist3', id=5, style='modern'),
]

vouchers_db = [
    Voucher(id=1, login='visitor1', amount_pictures=3, price=100, description="3 pictures for 100$", status='placed', style='realism'),
    Voucher(id=2, login='visitor2', amount_pictures=5, price=200, description="5 pictures for 200$", status='in work', style='impressionism'),
    Voucher(id=3, login='visitor3', amount_pictures=2, price=150, description="2 pictures for 150$", status='ready', style='modern'),
    Voucher(id=4, login='visitor2', amount_pictures=5, price=200, description="5 pictures for 200$", status='in work', style='impressionism'),
    Voucher(id=5, login='visitor2', amount_pictures=5, price=200, description="5 pictures for 200$", status='in work', style='impressionism'),
]

accounts_db = [
    Account(login='artist1', password='password123', surName='Smith', firstName='Alice', patronymic='Marie', email='alice@email.com', type_role='artist', phone='1234567890', sex='f', date_of_birth='1995-05-15'),
    Account(login='artist2', password='password456', surName='Johnson', firstName='Bob', patronymic='Marie', email='bob@email.com', type_role='visitor', phone='0987654321', sex='m', date_of_birth='1990-10-10'),
    Account(login='artist3', password='password123', surName='Dean', firstName='Amelia', patronymic='Marie', email='amelia@email.com', type_role='artist', phone='1234567890', sex='f', date_of_birth='1995-05-15'),
    Account(login='visitor1', password='password456', surName='Black', firstName='Adam', patronymic='Marie', email='adam@email.com', type_role='visitor', phone='0987654321', sex='m', date_of_birth='1990-10-10'),
    Account(login='visitor2', password='password123', surName='Fisher', firstName='Lily', patronymic='Marie', email='lily@email.com', type_role='artist', phone='1234567890', sex='f', date_of_birth='1995-05-15'),
    Account(login='visitor3', password='password456', surName='Gate', firstName='Artur', patronymic='Marie', email='artur@email.com', type_role='visitor', phone='0987654321', sex='m', date_of_birth='1990-10-10'),

]

visitors_db = [
    Visitor(login='visitor1', id=1, residence='Moscow, Red Square'),
    Visitor(login='visitor2', id=2, residence='Saint Petersburg, Nevsky Prospect'),
    Visitor(login='visitor3', id=3, residence='Yaroslavl, st/ Syrkova'),
    Visitor(login='visitor2', id=4, residence='Saint Petersburg, Nevsky Prospect'),
    Visitor(login='visitor3', id=5, residence='Yaroslavl, st/ Syrkova'),
]


def api_key():
    return "api_key"

def artist_vouchers_auth():
    return ["write:Artists", "read:Artists", "write:Visitors", "read:Visitors"]

AllowedStyles = Literal[
    "realism",
    "impressionism",
    "fauvism",
    "modern",
    "expressionism",
    "cubism",
    "futurism",
    "abstractionism",
    "dadaism",
    "pop-art"
]

@app.put("/Artists/{Vouchers_id}", response_model=Artist, tags=["Artists"])
async def update_artist(
    request: Request,
    voucher_id: int, 
    new_style: AllowedStyles
    ):
    login=request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in") 

    # Ищем посетителя по login
    existing_artist = next((artist for artist in artists_db if artist.id == voucher_id), None)
    
    if existing_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")

    # Проверяем, что логин пользователя совпадает с владельцем записи
    if existing_artist.login != login:
        raise HTTPException(status_code=403, detail="Access denied: You do not own this artist record")

    # Обновляем место жительства
    existing_artist.style = new_style  
    return existing_artist


@app.get("/Artists", response_model=List[Artist], tags=["Artists"])
async def find_artists_by_style(
    request: Request,
    style: Optional[List[str]] = Query(
        ##default=["realism"],
        default=None,
        description="Style values that need to be considered for filter",
        enum=[
            "realism",
            "impressionism",
            "fauvism",
            "modern",
            "expressionism",
            "cubism",
            "futurism",
            "abstractionism",
            "dadaism",
            "pop-art"
        ],
        title="Style"
    )
):
    login=request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in") 
    
    if style is not None and not style:
        raise HTTPException(status_code=400, detail="Invalid style value")
    
    # Если стиль не указан, возвращаем всех артистов
    if style is None:
        filtered_artists = artists_db
    else:
        # Фильтруем артистов на основе предоставленных стилей
        filtered_artists = [artist for artist in artists_db if artist.style in style]
    
    if not filtered_artists:
        raise HTTPException(status_code=404, detail="Artists not found")

    return filtered_artists
    

@app.get("/Artists/{artist_id}", response_model=Artist, tags=["Artists"])
async def get_artist_by_id(
    request: Request,
    artist_id: int = Path(..., description="ID of Artists to return")
):
    login=request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in") 

    artist = next((artist for artist in artists_db if artist.id == artist_id), None)
    ##artist = next((artist for artist in artists_db if artist.login == login), None)
    
    if artist is None:
        raise HTTPException(status_code=404, detail="Artists not found")
    
    return artist


#####################################################################################


@app.post("/Vouchers", response_model=Voucher, tags=["Vouchers"])
async def place_vouchers(
    request: Request,
    voucher: Voucher
):
    # Получаем логин из куки
    login = request.cookies.get('login')
    
    # Проверяем, что логин существует и не пустой
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in") 

    # Ищем посетителя по ID
    existing_visitor = next((visitor for visitor in visitors_db if visitor.login == login), None)
    
    if existing_visitor is None:
        raise HTTPException(status_code=404, detail="Visitor not found")
    
    # Получаем максимальный ID для нового ваучера
    max_id = max((v.id for v in vouchers_db), default=0)
    
    # Создаем новый предзаказ
    new_voucher = Voucher(
        id=max_id + 1,
        login=login,  # Используем логин из куки
        amount_pictures=voucher.amount_pictures,
        price=voucher.price,
        description=voucher.description,
        status="placed",
        style=voucher.style
    )
    
    # Добавляем новый предзаказ в базу данных
    vouchers_db.append(new_voucher)
    
    return new_voucher


@app.get("/Vouchers", response_model=List[Voucher], tags=["Vouchers"])
async def find_vouchers(
    request: Request,
    style: Optional[List[str]] = Query(
        default=None,
        description="Style values that need to be considered for filter",
        enum=[
            "realism",
            "impressionism",
            "fauvism",
            "modern",
            "expressionism",
            "cubism",
            "futurism",
            "abstractionism",
            "dadaism",
            "pop-art"
        ],
        title="Style"
    ),
    status: Optional[List[str]] = Query(
        default=None,
        description="Status values that need to be considered for filter",
        enum=[
            "placed",
            "in work",
            "ready"
        ],
        title="Status"
    )
):
    # Получаем логин из куки
    login = request.cookies.get('login')
    
    # Проверяем, что логин существует и не пустой
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in") 
    
    # Если ни стиль, ни статус не указаны, возвращаем все ваучеры
    if style is None and status is None:
        if not vouchers_db:
            raise HTTPException(status_code=404, detail="Vouchers not found")
        return vouchers_db
    
    # Фильтруем ваучеры по стилю и статусу
    filtered_vouchers = vouchers_db

    if style:
        filtered_vouchers = [voucher for voucher in vouchers_db if voucher.style in style] ##voucher for voucher in vouchers_db if voucher.status in status

    if status:
        filtered_vouchers = [voucher for voucher in vouchers_db if voucher.status in status]

    # Проверяем, есть ли отфильтрованные ваучеры
    if not filtered_vouchers:
        raise HTTPException(status_code=404, detail="Vouchers not found")

    return filtered_vouchers

@app.get("/Vouchers/{voucher_id}", response_model=Voucher, tags=["Vouchers"])
async def get_vouchers_by_id(
    request: Request,
    voucher_id: int = Path(..., description="ID of Vouchers to return")
):
    # Получаем логин из куки
    login = request.cookies.get('login')
    
    # Проверяем, что логин существует и не пустой
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in") 
    
    voucher = next((v for v in vouchers_db if v.id == voucher_id), None)
    
    if voucher is None:
        raise HTTPException(status_code=404, detail="Vouchers not found")
    
    return voucher

AllowedStatus = Literal[
    "placed",
    "in work",
    "ready"
]

@app.put("/Vouchers/{VouchersId}", response_model=Voucher, tags=["Vouchers"])
async def update_voucher(
    request: Request,
    voucher_id: int, 
    new_status: AllowedStatus
    ):

    login=request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in") 

    # Ищем посетителя по ID
    existing_artist = next((artist for artist in artists_db if artist.login == login), None)
    
    if existing_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")

    # Проверяем, что логин пользователя совпадает с владельцем записи
    if existing_artist.login != login:
        raise HTTPException(status_code=403, detail="Access denied: You do not own this artist record")

    for idx, existing_voucher in enumerate(vouchers_db):
        if existing_voucher.id == voucher_id:
            existing_voucher.status = new_status  # Обновляем только статус
            return existing_voucher
    raise HTTPException(status_code=404, detail="Voucher not found")


@app.delete("/Vouchers/{VouchersId}", tags=["Vouchers"])
async def delete_voucher(
    request: Request,
    VouchersId: int
    ):
    login=request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in") 
    
    # Ищем посетителя по ID
    existing_visitor = next((visitor for visitor in visitors_db if visitor.login == login), None)
    
    if existing_visitor is None:
        raise HTTPException(status_code=404, detail="Visitor not found")

    # Проверяем, что логин пользователя совпадает с владельцем записи
    if existing_visitor.login != login:
        raise HTTPException(status_code=403, detail="Access denied: You do not own this visitor record")

    # Находим индекс ваучера с указанным идентификатором
    voucher_index = next((index for index, voucher in enumerate(vouchers_db) if voucher.id == VouchersId), None)
    
    # Если ваучер не найден, возвращаем 404
    if voucher_index is None:
        raise HTTPException(status_code=404, detail="Vouchers not found")
    
    # Удаляем ваучер из базы данных
    vouchers_db.pop(voucher_index)
    
    return {"detail": "Vouchers deleted successfully"}


######################################################################################################


AllowedRols = Literal[
    "visitor",
    "artist"
]

@app.post("/Accounts", response_model=Account, tags=["Accounts"])
async def place_accounts(
    account: Account,
):
    
    if any(v.login == account.login for v in accounts_db):
        raise HTTPException(status_code=400, detail="Error login already exists.")
    
    # Создаем новый 
    new_account = Account(
        login=account.login,
        password=account.password,
        surName=account.surName,
        firstName=account.firstName,
        patronymic=account.patronymic,
        email=account.email,
        type_role=account.type_role,
        phone=account.phone,
        sex=account.sex,
        date_of_birth=account.date_of_birth
    )

    if (account.type_role == "artist"):
        new_artist = Artist(
            id=min((voucher.id for voucher in vouchers_db), default=0) - 1,
            login=account.login,
            style="realism"
        )
        artists_db.append(new_artist)

    if (account.type_role == "visitor"):
        new_visitor = Visitor(
            id=min((voucher.id for voucher in vouchers_db), default=0) - 1,
            login=account.login,
            residence="None"
        )
        visitors_db.append(new_visitor)
    
    # Добавляем новый предзаказ в базу данных
    accounts_db.append(new_account)
    
    return new_account


# Имитация хранилища для текущего пользователя (для примера)
current_user = None

class Credentials(BaseModel):
    login: str = Field(..., example='login')
    password: str = Field(..., example='password')

class Cookies(BaseModel):
    login: str | None = None


@app.post("/Accounts/login", tags=["Accounts"])
async def login(
    credentials:Credentials
):
    
    for account in accounts_db:
        if account.login == credentials.login and account.password == credentials.password:
            content = {"message": "Login successful"}
            response = JSONResponse(content=content)
            response.set_cookie(key="login", value=credentials.login)
            return response
    
    raise HTTPException(status_code=400, detail="Invalid login/password supplied")

@app.get("/Accounts/logout", tags=["Accounts"])
async def logout(
    request: Request,
    ##login: str = Cookie(None)
):
    login=request.cookies.get('login')

    if login is not (None or ""):
        content = {"message": "Logout successful"}
        response = JSONResponse(content=content)
        response.set_cookie(key="login", value="")
        return response
    else:
        raise HTTPException(status_code=400, detail="No user is currently logged in")

@app.get("/Accounts", response_model=List[Account], tags=["Accounts"])
async def get_accounts_by_name(
    request: Request,
    first_name: Optional[str] = Query(None, description="The first name to search for."),
    last_name: Optional[str] = Query(None, description="The last name to search for."),
    ##login: str = Cookie(None)  # Извлекаем логин из куки
):
    login=request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=400, detail="No user is currently logged in")

    results = []
    for account in accounts_db:
        if (first_name and account.firstName.lower() == first_name.lower()) and (last_name and account.surName.lower() == last_name.lower()):
            results.append(account)

    if not results:
        raise HTTPException(status_code=404, detail="Accounts not found")

    return results

@app.put("/Accounts", tags=["Accounts"])
async def update_account_name(
    request: Request,
    new_first_name: str = Query(..., description="New first name for the account"),
    new_last_name: str = Query(..., description="New last name for the account"),
    ##login: str = Cookie(None)  # Логин извлекается автоматически из куки
):
    login=request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=400, detail="No user is currently logged in")

    # Поиск аккаунта по логину
    account_to_update = next((account for account in accounts_db if account.login == login), None)

    if account_to_update is None:
        raise HTTPException(status_code=404, detail="Account not found")

    # Обновление имени и фамилии аккаунта
    account_to_update.firstName = new_first_name
    account_to_update.surName = new_last_name

    return {"message": "Account name updated successfully"}


@app.delete("/Accounts", tags=["Accounts"])
async def delete_account(
    request: Request,
    ##login: str = Cookie(None)
    ):  # Логин извлекается автоматически из куки
    login=request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=400, detail="No user is currently logged in")

    # Поиск аккаунта по логину
    account_to_delete = next((account for account in accounts_db if account.login == login), None)

    if account_to_delete is None:
        raise HTTPException(status_code=404, detail="Account not found")

    # Удаляем аккаунт из базы данных
    accounts_db.remove(account_to_delete)

    # Удаляем аккаунт из соответствующей базы данных в зависимости от роли
    if account_to_delete.type_role == "artist":
        artists_db[:] = [a for a in artists_db if a.login != login]
    elif account_to_delete.type_role == "visitor":
        visitors_db[:] = [v for v in visitors_db if v.login != login]

    return {"message": "Account deleted successfully"}


###########################################################################################


@app.put("/Visitors", response_model=Visitor, tags=["Visitors"])
async def update_visitor(
    request: Request,
    visitor_id: int, 
    new_residence: str,
    ##login: str = Cookie(None)  # Извлекаем логин из куки
):
    login=request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    # Ищем посетителя по ID
    existing_visitor = next((visitor for visitor in visitors_db if visitor.id == visitor_id), None)
    
    if existing_visitor is None:
        raise HTTPException(status_code=404, detail="Visitor not found")

    # Проверяем, что логин пользователя совпадает с владельцем записи
    if existing_visitor.login != login:
        raise HTTPException(status_code=403, detail="Access denied: You do not own this visitor record")

    # Обновляем место жительства
    existing_visitor.residence = new_residence  
    return existing_visitor

@app.get("/Visitors/{visitor_id}", response_model=Visitor, tags=["Visitors"])
async def get_visitor_by_id(
    request: Request,
    visitor_id: int = Path(..., description="ID of Visitor to return"),
    ##login: str = Cookie(None)  # Извлекаем логин из куки
):
    login=request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    # Ищем посетителя по ID
    visitor = next((visitor for visitor in visitors_db if visitor.id == visitor_id), None)
    
    if visitor is None:
        raise HTTPException(status_code=404, detail="Visitor not found")

    return visitor