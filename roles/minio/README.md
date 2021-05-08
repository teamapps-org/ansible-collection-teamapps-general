# MinIO S3 Server

S3 compatible service. Simple setup, standalone using docker-compose.yml

MinIO website: <https://min.io>

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
    minio_access_key: please_override
    minio_secret_key: FovMoghpokDiUnecshydhoolRipht6daiwofryt
  hosts:
    - minio1.example.com
  roles:
    - role: minio
~~~
