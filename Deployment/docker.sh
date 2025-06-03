#!/bin/bash

# Indonesian Shipping Price Checker - Docker Management Script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install it first."
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "🚚 Indonesian Shipping Price Checker - Docker Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start the application"
    echo "  dev         Start in development mode"
    echo "  stop        Stop the application"
    echo "  restart     Restart the application"
    echo "  build       Build the Docker images"
    echo "  logs        Show application logs"
    echo "  cli         Run CLI interface"
    echo "  test        Run system tests"
    echo "  clean       Clean up containers and images"
    echo "  status      Show container status"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start     # Start the web application on http://localhost:8501"
    echo "  $0 dev       # Start development server on http://localhost:8502"
    echo "  $0 cli       # Run interactive CLI"
    echo ""
}

# Function to start the application
start_app() {
    print_status "Starting Indonesian Shipping Price Checker..."
    docker-compose up shipping-app
    print_success "Application started! Access it at: http://localhost:8501"
}

# Function to start development mode
start_dev() {
    print_status "Starting development environment..."
    docker-compose --profile dev up -d
    print_success "Development server started! Access it at: http://localhost:8502"
}

# Function to stop the application
stop_app() {
    print_status "Stopping application..."
    docker-compose down
    print_success "Application stopped."
}

# Function to restart the application
restart_app() {
    print_status "Restarting application..."
    docker-compose restart
    print_success "Application restarted."
}

# Function to build images
build_images() {
    print_status "Building Docker images..."
    docker-compose build
    print_success "Images built successfully."
}

# Function to show logs
show_logs() {
    print_status "Showing application logs (Press Ctrl+C to exit)..."
    docker-compose logs -f shipping-app
}

# Function to run CLI
run_cli() {
    print_status "Starting CLI interface..."
    docker-compose --profile cli run --rm shipping-cli
}

# Function to run tests
run_tests() {
    print_status "Running system tests..."
    docker-compose exec shipping-app python test_system.py || \
    docker-compose run --rm shipping-app python test_system.py
}

# Function to clean up
clean_up() {
    print_warning "This will remove all containers and images. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up containers and images..."
        docker-compose down --rmi all --volumes --remove-orphans
        print_success "Cleanup completed."
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to show status
show_status() {
    print_status "Container status:"
    docker-compose ps
}

# Main script logic
main() {
    # Check prerequisites
    check_docker
    check_docker_compose
    
    # Handle commands
    case "${1:-help}" in
        start)
            start_app
            ;;
        dev)
            start_dev
            ;;
        stop)
            stop_app
            ;;
        restart)
            restart_app
            ;;
        build)
            build_images
            ;;
        logs)
            show_logs
            ;;
        cli)
            run_cli
            ;;
        test)
            run_tests
            ;;
        clean)
            clean_up
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
