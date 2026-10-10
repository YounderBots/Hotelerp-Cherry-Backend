// AttachmentPreview.jsx
//
// Renders a file the API stored for a record — an incident photo, a scanned
// report — inline in a View modal.
//
// WHY IT IS NOT JUST AN <img>
// Uploads are served by the same authenticated gateway proxy as the JSON API
// (`/hotel/templates/static/...`, `/masterdata/templates/static/...`), and a
// browser sends no Authorization header on a plain subresource request, so an
// <img src> or an <a href> pointed at one gets a 401 and renders as a broken
// image. The bytes are fetched here with the session token and served from an
// object URL instead, revoked when this unmounts or the path changes.
//
// This is the reason `mediaUrl()` in functions/apiHelpers.js carries a note
// saying stored images "still need a gateway route before they will actually
// load" — they do not; they need an authenticated fetch, which is this.
import React, { useEffect, useState } from 'react';
import { FileText } from 'lucide-react';
import APICall from '../APICalls/APICalls';
import './AttachmentPreview.css';

/** Last path segment of a stored upload, used as the display and download name. */
const attachmentName = (path) =>
  String(path ?? '').split('/').pop() || 'attachment';

/**
 * @param {string} path    stored path, e.g. "/templates/static/room_incidents/ab.png"
 * @param {string} prefix  gateway service prefix that fronts the static mount,
 *                         e.g. "/hotel" or "/masterdata"
 * @param {string} alt     accessible name for an image attachment
 */
const AttachmentPreview = ({ path, prefix = '', alt, className = '' }) => {
  const [state, setState] = useState({ status: 'loading', url: null, type: '', message: '' });

  useEffect(() => {
    if (!path) return undefined;

    let alive = true;
    let objectUrl = null;

    // The state transition is deferred to a microtask so nothing is set
    // synchronously inside the effect — the same reason useApiResource does it,
    // and what keeps React 19 from charging an extra render pass here.
    Promise.resolve()
      .then(() => {
        if (!alive) return null;
        setState({ status: 'loading', url: null, type: '', message: '' });
        const suffix = path.startsWith('/') ? path : `/${path}`;
        return APICall.getBlobT(`${prefix}${suffix}`);
      })
      .then((blob) => {
        if (!alive || !blob) return;
        objectUrl = URL.createObjectURL(blob);
        setState({ status: 'ready', url: objectUrl, type: blob.type || '', message: '' });
      })
      .catch((err) => {
        if (!alive) return;
        setState({
          status: 'error',
          url: null,
          type: '',
          message: err?.message || 'The attachment could not be loaded.',
        });
      });

    return () => {
      alive = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [path, prefix]);

  if (!path) return null;

  const wrapperClass = ['attachment', className].filter(Boolean).join(' ');
  const name = attachmentName(path);

  if (state.status === 'loading') {
    return (
      <span className={`${wrapperClass} attachment__note`} role="status">
        Loading attachment…
      </span>
    );
  }

  if (state.status === 'error') {
    return (
      <span className={`${wrapperClass} attachment__note attachment__note--error`} role="alert">
        {state.message}
      </span>
    );
  }

  // Images preview in place.
  if (state.type.startsWith('image/')) {
    return (
      <a className={wrapperClass} href={state.url} target="_blank" rel="noreferrer" title={name}>
        <img className="attachment__image" src={state.url} alt={alt || name} />
      </a>
    );
  }

  // PDFs render in the browser's own viewer inside a bounded frame, because a
  // clerk checking an identity document should not have to download and reopen
  // it. `<object>` rather than `<iframe>` specifically because its CHILDREN are
  // the fallback: where no PDF plugin exists -- iOS Safari, a locked-down kiosk
  // -- the frame shows the download row instead of a blank box. `<iframe>` can
  // only show its own fallback on a load failure, which a plugin-less browser
  // never raises: it just renders an empty rectangle.
  if (state.type === 'application/pdf') {
    return (
      <div className={`${wrapperClass} attachment__pdf-block`}>
        <object
          className="attachment__pdf"
          data={state.url}
          type="application/pdf"
          aria-label={alt || `${name} (PDF preview)`}
        >
          <a className="attachment__file" href={state.url} download={name}>
            <FileText size={16} aria-hidden="true" />
            <span className="attachment__file-name">{name}</span>
          </a>
        </object>
        <a className="attachment__file" href={state.url} download={name}>
          <FileText size={16} aria-hidden="true" />
          <span className="attachment__file-name">{name}</span>
        </a>
      </div>
    );
  }

  return (
    <a className={`${wrapperClass} attachment__file`} href={state.url} download={name}>
      <FileText size={16} aria-hidden="true" />
      <span className="attachment__file-name">{name}</span>
    </a>
  );
};

export default AttachmentPreview;
