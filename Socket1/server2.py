# server2.py
import socket
import sys
import threading

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

def handle_client(client_socket, client_address):
    """
    This function is executed in a new thread for each client connection.
    It handles all communication with that single client.
    """
    print(f"{bcolors.OKGREEN}[THREAD {threading.get_ident()}] Accepted connection from {client_address}{bcolors.ENDC}")
    try:
        while True:
            # Receive data from the client
            data = client_socket.recv(1024)
            if not data:
                print(f"{bcolors.FAIL}[THREAD {threading.get_ident()}] Client {client_address} disconnected.{bcolors.ENDC}")
                break
            
            expression = data.decode('utf-8')
            print(f"{bcolors.OKBLUE}[THREAD {threading.get_ident()}] Received from {client_address}: '{expression}'{bcolors.ENDC}")

            # Evaluate expression and send result back
            result = evaluate_expression(expression)
            print(f"{bcolors.OKBLUE}[THREAD {threading.get_ident()}] Sending reply to {client_address}: '{result}'{bcolors.ENDC}")
            client_socket.sendall(result.encode('utf-8'))

    except ConnectionResetError:
        print(f"{bcolors.FAIL}[THREAD {threading.get_ident()}] Client {client_address} forcefully closed the connection.{bcolors.ENDC}")
    except Exception as e:
        print(f"{bcolors.FAIL}[THREAD {threading.get_ident()}] An error occurred with {client_address}: {e}{bcolors.ENDC}")
    finally:
        # Close the client socket when the loop is broken
        client_socket.close()
        print(f"{bcolors.WARNING}[THREAD {threading.get_ident()}] Closed connection to {client_address}.{bcolors.ENDC}")

def run_server(ip, port):
    """
    Runs a multi-threaded server that can handle multiple clients concurrently.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((ip, port))
        # Listen for connections, with a backlog of 5
        server_socket.listen(5)
        print(f"{bcolors.OKGREEN}Multi-threaded server listening on {ip}:{port}...{bcolors.ENDC}")

        # Main server loop to accept new connections
        while True:
            # Accept a new connection. This is a blocking call.
            client_socket, client_address = server_socket.accept()
            
            # Create a new thread to handle the client
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True # Allows main thread to exit even if client threads are running
            client_thread.start()

    except OSError as e:
        print(f"{bcolors.FAIL}Error: Could not bind to port {port}. It might be already in use. {e}{bcolors.ENDC}")
    except KeyboardInterrupt:
        print(f"\n{bcolors.WARNING}Server is shutting down.{bcolors.ENDC}")
    finally:
        print(f"{bcolors.WARNING}Closing server socket.{bcolors.ENDC}")
        server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python server2.py <ip_address> <port>")
        sys.exit(1)
    
    IP_ADDRESS = sys.argv[1]
    try:
        PORT = int(sys.argv[2])
    except ValueError:
        print("Error: Port must be an integer.")
        sys.exit(1)

    run_server(IP_ADDRESS, PORT)
