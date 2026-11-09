# MinIO S3 Server

S3 compatible service. Simple setup, standalone using docker-compose.yml

MinIO website: <https://min.io>

## Container image

`minio_image` selects the image repository and defaults to `minio/minio`.
`minio_version` selects its tag. Point `minio_image` at a private registry
mirror to keep using a release that is no longer available upstream.

Upstream `minio/minio` is archived and gets no security fixes. The
`cgr.dev/chainguard/minio` image builds the maintained
[chainguard-forks/minio](https://github.com/chainguard-forks/minio). Its free
tier publishes only `latest`, so pin it by digest:
`minio_image: cgr.dev/chainguard/minio` and
`minio_version: latest@sha256:<digest>`.

That image runs as uid `65532`. MinIO fails with "Unable to write to the
backend" on data created by the root-running upstream image. Either set
`minio_container_user: '0:0'` or change the owner of `minio_data_path` to
`65532`.

The healthcheck runs `mc ready local`, which both images include.

## Role Variables

See `default/main.yml`

Dependencies
------------

Docker, docker-compose. Designed for use with webproxy role

## Example Playbook

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

~~~yaml
- name: Minio S3 Play
  vars:
    minio_domain: minio.example.com
    minio_root_user: please_override
    minio_root_password: GenerateYourSecretPassword!!
  hosts:
    - minio1.example.com
  roles:
    - role: minio
~~~
