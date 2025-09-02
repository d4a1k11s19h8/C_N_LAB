# client.py
import socket
import sys

# A small utility for color-coding terminal output
class bcolors:
    """A class to hold ANSI escape codes for terminal colors."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def run_client(server_ip, server_port):
    """
    Main function to run the TCP client.
    Connects to the server and enters a loop to send/receive messages.
    """
    # Create a TCP/IP socket using IPv4
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect the socket to the server's address and port
        print(f"{bcolors.WARNING}Attempting to connect to {server_ip}:{server_port}...{bcolors.ENDC}")
        client_socket.connect((server_ip, server_port))
        print(f"{bcolors.OKGREEN}Successfully connected to the server.{bcolors.ENDC}")

        # Main loop to send and receive data
        while True:
            # Prompt user for an arithmetic expression
            message = input(f"{bcolors.OKCYAN}Enter expression (e.g., '9 + 8') or Ctrl+C to exit: {bcolors.ENDC}")
            
            if not message:
                continue

            # Send the user's message to the server, encoded as bytes
            print(f"{bcolors.OKBLUE}Sending: '{message}'{bcolors.ENDC}")
            client_socket.sendall(message.encode('utf-8'))

            # Wait for and receive the server's reply (up to 1024 bytes)
            data = client_socket.recv(1024)
            if not data:
                # If recv returns an empty string, the server has closed the connection
                print(f"{bcolors.FAIL}Server closed the connection.{bcolors.ENDC}")
                break
            
            # Decode the reply from bytes to string and display it
            reply = data.decode('utf-8')
            print(f"{bcolors.OKGREEN}Server replied: {reply}{bcolors.ENDC}\n")

    except ConnectionRefusedError:
        print(f"{bcolors.FAIL}Connection refused. Is the server running at {server_ip}:{server_port}?{bcolors.ENDC}")
    except KeyboardInterrupt:
        # Handle Ctrl+C to gracefully exit the client
        print(f"\n{bcolors.WARNING}Client is shutting down.{bcolors.ENDC}")
    except Exception as e:
        print(f"{bcolors.FAIL}An error occurred: {e}{bcolors.ENDC}")
    finally:
        # Ensure the socket is always closed on exit
        print(f"{bcolors.WARNING}Closing client socket.{bcolors.ENDC}")
        client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_ip> <server_port>")
        sys.exit(1)
    
    SERVER_IP = sys.argv[1]
    try:
        SERVER_PORT = int(sys.argv[2])
    except ValueError:
        print("Error: Port must be an integer.")
        sys.exit(1)

    run_client(SERVER_IP, SERVER_PORT)
