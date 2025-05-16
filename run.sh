#!/bin/bash

function show_usage() {
    echo "Usage: ./run.sh [dev|prod] [up|down|logs|build|shell]"
    echo "Examples:"
    echo "  ./run.sh dev up     # Start development environment"
    echo "  ./run.sh prod up    # Start production environment"
    echo "  ./run.sh dev down   # Stop development environment"
    echo "  ./run.sh dev logs   # View development logs"
    echo "  ./run.sh dev shell  # Open shell in app container"
}

if [ $# -lt 2 ]; then
    show_usage
    exit 1
fi

ENV=$1
ACTION=$2
COMPOSE_FILE="docker/$ENV/docker-compose.yml"

# Map environment names to their file names
if [ "$ENV" = "dev" ]; then
    ENV_FILE="env/development.env"
elif [ "$ENV" = "prod" ]; then
    ENV_FILE="env/production.env"
else
    echo "Error: Invalid environment '$ENV'"
    show_usage
    exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "Error: Environment '$ENV' not found"
    show_usage
    exit 1
fi

if [ ! -f "$ENV_FILE" ] && [ "$ENV" = "dev" ]; then
    echo "Creating development environment file from example..."
    cp env/example.env "$ENV_FILE"
fi

if [ ! -f "$ENV_FILE" ] && [ "$ENV" = "prod" ]; then
    echo "Error: Production environment file not found"
    echo "Please create env/production.env with appropriate settings"
    exit 1
fi

function build_base_image() {
    echo "Building base image..."
    docker build -t excel-data-processor-base:latest -f docker/Dockerfile.base .
}

function check_prod_env() {
    if [ "$ENV" = "prod" ]; then
        if [ ! -f "env/production.env" ]; then
            echo "Error: Production environment file not found"
            exit 1
        fi
        
        # Check for required environment variables
        required_vars=("DB_USER" "DB_PASSWORD" "SECRET_KEY" "MYSQL_ROOT_PASSWORD")
        for var in "${required_vars[@]}"; do
            if ! grep -q "^$var=" "env/production.env"; then
                echo "Error: $var is not set in production.env"
                exit 1
            fi
        done
    fi
}

function init_localstack() {
    if [ "$ENV" = "dev" ]; then
        echo "Waiting for LocalStack to be ready..."
        # Try up to 30 times (60 seconds total)
        for i in {1..30}; do
            if docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec -T localstack awslocal s3 ls &> /dev/null; then
                echo "LocalStack is ready. Creating S3 bucket..."
                
                # Create the S3 bucket
                docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec -T localstack awslocal s3 mb s3://local-excel-bucket
                
                # Set bucket policy to public-read
                docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec -T localstack awslocal s3api put-bucket-acl --bucket local-excel-bucket --acl public-read
                
                echo "S3 bucket 'local-excel-bucket' created successfully"
                return 0
            fi
            echo "Waiting for LocalStack to be ready... (attempt $i/30)"
            sleep 2
        done
        echo "Error: LocalStack failed to start within 60 seconds"
        return 1
    fi
}

case $ACTION in
    up)
        check_prod_env
        build_base_image
        if [ "$ENV" = "prod" ]; then
            docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
        else
            docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
            init_localstack
        fi
        ;;
    down)
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down
        ;;
    logs)
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs -f
        ;;
    build)
        check_prod_env
        build_base_image
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE build
        ;;
    shell)
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec app /bin/bash
        ;;
    *)
        show_usage
        exit 1
        ;;
esac 