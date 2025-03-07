project := `basename "$PWD"`

list:
    just --list

# can run `just start-server` or `just start-server -d` for detach mode. 
start-server *args:
    docker run \
        {{args}} \
        -v ~/.letta/.persist/{{project}}:/var/lib/postgresql/data \
        -p 8283:8283 \
        -e OPENAI_API_KEY="$OPENAI_API_KEY" \
        --name {{project}}_letta_server \
        letta/letta:latest

# to stop letta server when running in detach mode
stop-server:
    docker stop {{project}}_letta_server

clear-cache:
    rm -rf ~/.letta/.persist/{{project}}
