# server1.py
import socket
import sys

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
    Runs an iterative server that handles one client at a time.
    """
    # Create a TCP/IP socket using IPv4
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow reusing the address to avoid "Address already in use" errors
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # Bind the socket to the given IP and port
        server_socket.bind((ip, port))
        # Start listening for incoming connections (backlog of 1 is enough for this server)
        server_socket.listen(1)
        print(f"{bcolors.OKGREEN}Server listening on {ip}:{port}...{bcolors.ENDC}")

        # Main server loop to accept clients one by one
        while True:
            print(f"{bcolors.WARNING}\nWaiting for a new client connection...{bcolors.ENDC}")
            # Accept a new connection. This is a blocking call.
            client_socket, client_address = server_socket.accept()
            
            # Using 'with' ensures the client_socket is closed automatically
            with client_socket:
                print(f"{bcolors.OKGREEN}Accepted connection from {client_address}{bcolors.ENDC}")
                
                # Loop to handle all messages from the connected client
                while True:
                    # Receive data from the client (up to 1024 bytes)
                    data = client_socket.recv(1024)
                    if not data:
                        # If data is empty, the client has closed the connection
                        print(f"{bcolors.FAIL}Client {client_address} disconnected.{bcolors.ENDC}")
                        break
                    
                    expression = data.decode('utf-8')
                    print(f"{bcolors.OKBLUE}Received from {client_address}: '{expression}'{bcolors.ENDC}")

                    # Evaluate the expression
                    result = evaluate_expression(expression)
                    
                    # Send the result back to the client
                    print(f"{bcolors.OKBLUE}Sending reply to {client_address}: '{result}'{bcolors.ENDC}")
                    client_socket.sendall(result.encode('utf-8'))

    except OSError as e:
        print(f"{bcolors.FAIL}Error: Could not bind to port {port}. It might be already in use. {e}{bcolors.ENDC}")
    except KeyboardInterrupt:
        print(f"\n{bcolors.WARNING}Server is shutting down.{bcolors.ENDC}")
    finally:
        # Ensure the server socket is always closed on exit
        print(f"{bcolors.WARNING}Closing server socket.{bcolors.ENDC}")
        server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python server1.py <ip_address> <port>")
        sys.exit(1)
    
    IP_ADDRESS = sys.argv[1]
    try:
        PORT = int(sys.argv[2])
    except ValueError:
        print("Error: Port must be an integer.")
        sys.exit(1)

    run_server(IP_ADDRESS, PORT)
