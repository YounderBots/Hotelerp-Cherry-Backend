// AuthedImage.jsx
//
// An <img> for a file the API stored — a room photo, a menu tile — shown
// outside a form field.
//
// WHY IT IS NOT JUST AN <img src>
// Uploads sit behind the same authenticated gateway proxy as the JSON API
// (`/masterdata/templates/static/upload_image/...`), and a browser sends no
// Authorization header on a plain subresource request. Pointing an <img> at
// one gets a 401/403 and renders as a broken image — which is exactly what
// the Room View grid did for every room in the property.
//
// ImagePicker already fetches a stored path with the session token, but it is
// a FORM FIELD: label, empty-slot chrome, replace/clear controls. A card
// thumbnail needs the bytes without the field around them. Both go through
// hooks/useAuthedMedia, so there is one fetch-and-revoke implementation.
//
// While the bytes are loading, and if they fail, `fallback` is rendered in the
// image's place — a record whose photo cannot be loaded must not silently read
// as a record with no photo, so pass a fallback that says as much.
import React from 'react';

import useAuthedMedia from '../hooks/useAuthedMedia';

const AuthedImage = ({
  /** Stored path ("/templates/static/…"), an absolute URL, or null. */
  path,
  /** Gateway service prefix fronting the static mount, e.g. "/masterdata". */
  prefix = '',
  alt = '',
  className = '',
  /** Rendered while loading, on failure, and when there is no path at all. */
  fallback = null,
  ...imgProps
}) => {
  const { url, status } = useAuthedMedia(path || null, prefix);

  if (!path || status === 'error' || !url) return fallback;

  return <img src={url} alt={alt} className={className} {...imgProps} />;
};

export default AuthedImage;
