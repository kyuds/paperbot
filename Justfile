project := `basename "$PWD"`

list:
    just --list

start-server:
    docker run \
        -v ~/.letta/.persist/{{project}}:/var/lib/postgresql/data \
        -p 8283:8283 \
        -e OPENAI_API_KEY="$OPENAI_API_KEY" \
        letta/letta:latest

clear-cache:
    rm -rf ~/.letta/.persist/{{project}}
