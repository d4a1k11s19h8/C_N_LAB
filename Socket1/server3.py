# server3.py
import socket
import sys
import select

# A small utility for color-coding terminal output
class bcolors:
    """A class to hold ANSI escape codes for terminal colors."""
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def evaluate_expression(expression):
    """
    Evaluates a simple arithmetic expression string.
    Returns the result as a string or an error message.
    """
    try:
        parts = expression.split()
        if len(parts) != 3:
            return "Error: Invalid expression format. Use 'operand1 operator operand2'"
        
        operand1 = float(parts[0])
        operator = parts[1]
        operand2 = float(parts[2])

        if operator == '+':
            return str(operand1 + operand2)
        elif operator == '-':
            return str(operand1 - operand2)
        elif operator == '*':
            return str(operand1 * operand2)
        elif operator == '/':
            if operand2 == 0:
                return "Error: Division by zero"
            return str(operand1 / operand2)
        else:
            return "Error: Unsupported operator"
    except ValueError:
        return "Error: Invalid numbers in expression"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def run_server(ip, port):
    """
    Runs a single-process concurrent server using the 'select' module.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(0)  # Set to non-blocking mode

    try:
        server_socket.bind((ip, port))
        server_socket.listen(5)
        print(f"{bcolors.OKGREEN}Select-based calculator server listening on {ip}:{port}...{bcolors.ENDC}")

        # Sockets from which we expect to read
        inputs = [server_socket]

        while inputs:
            # select() blocks until at least one file descriptor is ready
            readable, _, exceptional = select.select(inputs, [], inputs)

            for s in readable:
                if s is server_socket:
                    # A "readable" server socket means a new connection is waiting
                    client_socket, client_address = s.accept()
                    print(f"{bcolors.OKGREEN}Accepted new connection from {client_address}{bcolors.ENDC}")
                    client_socket.setblocking(0)
                    inputs.append(client_socket)
                else:
                    # An existing client socket is "readable"
                    data = s.recv(1024)
                    if data:
                        expression = data.decode('utf-8')
                        client_addr = s.getpeername()
                        print(f"{bcolors.OKBLUE}Received from {client_addr}: '{expression}'{bcolors.ENDC}")
                        
                        result = evaluate_expression(expression)
                        print(f"{bcolors.OKBLUE}Sending reply to {client_addr}: '{result}'{bcolors.ENDC}")
                        s.sendall(result.encode('utf-8'))
                    else:
                        # An empty read means the client disconnected
                        client_addr = s.getpeername()
                        print(f"{bcolors.FAIL}Client {client_addr} disconnected.{bcolors.ENDC}")
                        inputs.remove(s)
                        s.close()
            
            for s in exceptional:
                # Handle exceptional conditions
                client_addr = s.getpeername()
                print(f"{bcolors.FAIL}Exceptional condition for {client_addr}. Closing connection.{bcolors.ENDC}")
                inputs.remove(s)
                s.close()

    except OSError as e:
        print(f"{bcolors.FAIL}Error: Could not bind to port {port}. It might be already in use. {e}{bcolors.ENDC}")
    except KeyboardInterrupt:
        print(f"\n{bcolors.WARNING}Server is shutting down.{bcolors.ENDC}")
    finally:
        print(f"{bcolors.WARNING}Closing server socket.{bcolors.ENDC}")
        server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python server3.py <ip_address> <port>")
        sys.exit(1)
    
    IP_ADDRESS = sys.argv[1]
    try:
        PORT = int(sys.argv[2])
    except ValueError:
        print("Error: Port must be an integer.")
        sys.exit(1)

    run_server(IP_ADDRESS, PORT)
