import asyncio
from app.main import app
from app.core.database import get_connection

async def test_all_routes():
    print("\n=== TESTING ALL ROUTES ===")
    openapi = app.openapi()
    
    # We will test all GET routes
    routes_to_test = []
    for path, methods in openapi['paths'].items():
        if 'get' in methods:
            routes_to_test.append(path)
            
    # Sample IDs from DB for parameterized routes
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id_solicitud FROM solicitudes_compensacion LIMIT 1")
    row_sol = c.fetchone()
    sample_sol_id = row_sol[0] if row_sol else 1

    c.execute("SELECT id_empleado FROM empleados LIMIT 1")
    row_emp = c.fetchone()
    sample_emp_id = row_emp[0] if row_emp else 1
    conn.close()

    failures = []
    
    for path in routes_to_test:
        test_path = path
        query_str = b""
        if "{id_solicitud}" in test_path:
            test_path = test_path.replace("{id_solicitud}", str(sample_sol_id))
        if "{id_anexo}" in test_path:
            # Test anexos 1 through 10
            anexo_paths = [path.replace("{id_anexo}", str(i)) for i in range(1, 11)]
        else:
            anexo_paths = [test_path]
            
        for p in anexo_paths:
            # Handle query params if needed
            if p == "/vacaciones/api/saldo":
                query_str = f"id_empleado={sample_emp_id}".encode()
            else:
                query_str = b""

            scope = {
                'type': 'http',
                'method': 'GET',
                'path': p,
                'raw_path': p.encode(),
                'query_string': query_str,
                'headers': [(b'host', b'localhost')],
                'client': ('127.0.0.1', 12345),
                'server': ('127.0.0.1', 8000),
                'scheme': 'http',
                'http_version': '1.1',
            }
            status_code = None
            response_body = []
            
            async def receive():
                return {'type': 'http.request', 'body': b'', 'more_body': False}
                
            async def send(message):
                nonlocal status_code
                if message['type'] == 'http.response.start':
                    status_code = message['status']
                elif message['type'] == 'http.response.body':
                    response_body.append(message.get('body', b''))

            try:
                await app(scope, receive, send)
                body = b''.join(response_body).decode('utf-8', errors='ignore')
                if status_code != 200:
                    failures.append((p, status_code, body[:300]))
                    print(f"[FAIL] {p} -> Status {status_code}: {body[:150]}")
                else:
                    print(f"[OK]   {p} -> Status 200 ({len(body)} bytes)")
            except Exception as e:
                failures.append((p, "EXCEPTION", str(e)))
                print(f"[EXC]  {p} -> Exception: {e}")

    print(f"\nTotal endpoints tested: {len(routes_to_test) + 9}")
    print(f"Total failures: {len(failures)}")
    for f in failures:
        print(f"  FAILED: {f}")

if __name__ == "__main__":
    asyncio.run(test_all_routes())
