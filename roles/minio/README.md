# MinIO S3 Server

S3 compatible service. Simple setup, standalone using docker-compose.yml

MinIO website: <https://min.io>

## Container image

Upstream `minio/minio` is archived and gets no security fixes. The role
defaults to `cgr.dev/chainguard/minio`, which builds the maintained
[chainguard-forks/minio](https://github.com/chainguard-forks/minio).

- `minio_image` selects the image repository. Point it at a private registry
  mirror to keep using an image that is no longer available upstream.
- `minio_version` selects the tag and defaults to `latest`. Chainguard's free
  tier publishes only `latest`, so pin a release by digest:
  `minio_version: latest@sha256:<digest>`.
- `minio_container_user` sets the container user and defaults to `'0:0'`. The
  Chainguard image runs as uid `65532`, but the data directory this role
  creates, and data written by the upstream image, are owned by root. Without
  root, MinIO fails with "Unable to write to the backend". To run as uid
  `65532`, change the owner of `minio_data_path` to `65532` and set
  `minio_container_user: ''`.

The healthcheck runs `mc ready local`, which both the Chainguard and the
upstream images include.

### Upgrading from `minio/minio`

Data written by `minio/minio` works with the Chainguard image unchanged. If
you set `minio_version` to an upstream `RELEASE.*` tag without setting
`minio_image`, that tag does not exist on `cgr.dev`. Either drop
`minio_version`, pin a Chainguard digest, or set `minio_image: minio/minio`
to stay on the upstream image.

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
