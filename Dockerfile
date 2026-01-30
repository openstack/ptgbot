
FROM quay.io/opendevorg/python-builder:3.12-trixie as builder

COPY . /tmp/src
RUN assemble

FROM quay.io/opendevorg/python-base:3.12-trixie as ptgbot

COPY --from=builder /output/ /output
RUN /output/install-from-bindep

COPY init.sh init.sh
CMD ./init.sh
