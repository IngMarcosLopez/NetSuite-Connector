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
    d = nt.query("SELECT * FROM OA_tables")
    print(d.__dict__)
    assert d.status == 200
