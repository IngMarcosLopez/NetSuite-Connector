env_params = dict(
    account_id="*****",
    user_email="*****",
    role_id="*****",
    dsn="*****",
    password="*****",
)


def test_make_query_success():
    from NetSuite_Connector.ODBC import ODBC

    nt = ODBC(**env_params)
    q = nt.query("SELECT * FROM OA_tables")
    print(q.__dict__)
    assert q.status == 200
