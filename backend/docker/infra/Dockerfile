# syntax=docker/dockerfile:1.7

FROM alpine:3.21 AS downloader

ARG TERRAFORM_VERSION=1.12.2
ARG KUBECTL_VERSION=v1.33.0
ARG HELM_VERSION=v3.18.3
ARG YQ_VERSION=v4.44.5

RUN apk add --no-cache curl unzip tar

RUN curl -fsSL "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" -o /tmp/terraform.zip \
  && unzip /tmp/terraform.zip -d /tmp/bin

RUN curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" -o /tmp/bin/kubectl \
  && chmod +x /tmp/bin/kubectl

RUN curl -fsSL "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz" -o /tmp/helm.tgz \
  && tar -xzf /tmp/helm.tgz -C /tmp \
  && mv /tmp/linux-amd64/helm /tmp/bin/helm \
  && chmod +x /tmp/bin/helm

RUN curl -fsSL "https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_amd64" -o /tmp/bin/yq \
  && chmod +x /tmp/bin/yq

FROM alpine:3.21

RUN addgroup -S infra && adduser -S infra -G infra \
  && apk add --no-cache bash ca-certificates git jq openssl

COPY --from=downloader /tmp/bin/terraform /usr/local/bin/terraform
COPY --from=downloader /tmp/bin/kubectl /usr/local/bin/kubectl
COPY --from=downloader /tmp/bin/helm /usr/local/bin/helm
COPY --from=downloader /tmp/bin/yq /usr/local/bin/yq
COPY docker/infra/entrypoint.sh /usr/local/bin/infra-run

RUN chmod +x /usr/local/bin/infra-run \
  && mkdir -p /workspace \
  && chown -R infra:infra /workspace

USER infra
WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/infra-run"]
CMD ["qc"]
