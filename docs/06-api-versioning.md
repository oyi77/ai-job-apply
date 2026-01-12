# API Versioning Strategy

This document outlines the API versioning strategy for the AI Job Application Assistant API.

## Versioning Scheme

The API uses a URL-based versioning scheme. The API version is specified in the URL, as shown in the following example:

```
/api/v1
```

In this example, the API version is `v1`.

## Major, Minor, and Patch Versions

The API version is composed of a major, minor, and patch version.

*   **Major Version:** The major version is incremented when there are breaking changes to the API. For example, if a new version of the API removes an endpoint or changes the request or response format of an existing endpoint, the major version will be incremented.

*   **Minor Version:** The minor version is incremented when there are new features or non-breaking changes to the API. For example, if a new version of the API adds a new endpoint or adds a new field to the response of an existing endpoint, the minor version will be incremented.

*   **Patch Version:** The patch version is incremented when there are bug fixes or other non-breaking changes to the API. For example, if a new version of the API fixes a bug in an existing endpoint, the patch version will be incremented.

## Specifying the API Version

The API version is specified in the URL of the request. For example, to access version 1.0.0 of the API, you would use the following URL:

```
/api/v1.0.0
```

If you do not specify a patch version, the latest patch version will be used. For example, if the latest patch version is 1.0.1, the following URL will be equivalent to `/api/v1.0.1`:

```
/api/v1.0
```

If you do not specify a minor or patch version, the latest minor and patch version will be used. For example, if the latest minor version is 1.1.0 and the latest patch version is 1.1.2, the following URL will be equivalent to `/api/v1.1.2`:

```
/api/v1
```

## Deprecation Policy

When a new major version of the API is released, the previous major version will be deprecated. The deprecated version will continue to be supported for a period of six months. After six months, the deprecated version will be removed.
