
FROM opendevorg/python-builder:3.9 as builder

COPY . /tmp/src
RUN assemble

FROM opendevorg/python-base:3.9 as ptgbot

COPY --from=builder /output/ /output
RUN /output/install-from-bindep

COPY init.sh init.sh
CMD ./init.sh
