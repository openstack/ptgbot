
FROM docker.io/opendevorg/python-builder:3.11-bookworm as builder

COPY . /tmp/src
RUN assemble

FROM docker.io/opendevorg/python-base:3.11-bookworm as ptgbot

COPY --from=builder /output/ /output
RUN /output/install-from-bindep

COPY init.sh init.sh
CMD ./init.sh
