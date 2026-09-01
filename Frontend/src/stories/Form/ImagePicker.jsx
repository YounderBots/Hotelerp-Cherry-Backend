// ImagePicker.jsx
//
// A single image slot: shows the current image (an already-uploaded URL or a
// freshly picked File), lets the user replace or clear it, and keeps the same
// label/spacing as every other field in a form.
//
// It replaces the bare `<input type="file">` the Rooms screen rendered under a
// hand-styled dashed box — unstyled default browser chrome sitting inside an
// otherwise themed form, with no way to remove a picked file and an
// object URL per render that was never revoked.
import React, { useEffect, useId, useMemo, useRef, useState } from 'react';
import { ImagePlus, Trash2 } from 'lucide-react';
import useAuthedMedia from '../../hooks/useAuthedMedia';
import './ImagePicker.css';

const ImagePicker = ({
  label,
  /** A File (newly picked) or a string URL (already stored) or null. */
  value,
  onChange,
  onClear,
  accept = 'image/*',
  disabled = false,
  /** Read-only display, used by View modals. */
  readOnly = false,
  /**
   * Gateway service prefix that fronts the static mount for a STORED path
   * ("/masterdata", "/user", "/hotel"). Supply this whenever `value` can be a
   * server path: uploads sit behind the authenticated proxy, and a plain
   * <img src> carries no Authorization header, so without it the browser is
   * answered 401 and the slot renders empty. With it, the bytes are fetched
   * with the session token and shown from an object URL.
   */
  authPrefix = '',
}) => {
  const inputRef = useRef(null);
  const inputId = useId();

  const isFile = value instanceof File;

  // A File needs an object URL to preview. Derived once per value and revoked
  // when the value changes or the component unmounts — calling
  // URL.createObjectURL(file) inline in the JSX, as the Rooms screen used to,
  // leaked one blob per render.
  const filePreview = useMemo(
    () => (isFile ? URL.createObjectURL(value) : null),
    [isFile, value],
  );

  useEffect(() => {
    if (!filePreview) return undefined;
    return () => URL.revokeObjectURL(filePreview);
  }, [filePreview]);

  // A stored path is fetched with the session token when the caller says which
  // service fronts it; otherwise it is used as-is (an absolute URL, or a slot
  // whose caller has already resolved it).
  const storedPath = !isFile && typeof value === 'string' && value ? value : null;
  const media = useAuthedMedia(authPrefix ? storedPath : null, authPrefix);

  const preview = isFile
    ? filePreview
    : authPrefix
      ? media.url
      : storedPath;

  // A stored path can still fail to load. Fall back to the empty-slot
  // treatment rather than leaving the browser's broken-image glyph in the
  // layout. Recording WHICH src failed means a new value clears the state on
  // its own, with no effect needed to reset it.
  const [failedSrc, setFailedSrc] = useState(null);
  const failed =
    (!!preview && preview === failedSrc) || (!!authPrefix && media.status === 'error');
  const loading = !!authPrefix && media.status === 'loading';
  const shown = failed ? null : preview;

  // What the empty slot says. "Choose image" is only right when there is
  // nothing stored; a record that HAS a photo the viewer cannot load must not
  // read as a record with no photo.
  const placeholder = loading
    ? 'Loading…'
    : failed
      ? 'Image unavailable'
      : readOnly
        ? 'No image'
        : 'Choose image';

  const handleFile = (e) => {
    const file = e.target.files?.[0];
    if (file) onChange?.(file);
    // Reset so picking the same file twice in a row still fires a change.
    e.target.value = '';
  };

  const openPicker = () => {
    if (!disabled && !readOnly) inputRef.current?.click();
  };

  // "Replace" rather than "Upload" depends on whether a value EXISTS, not on
  // whether it could be displayed — a photo that failed to load is still there
  // and picking a new file still replaces it.
  const hasValue = isFile || !!storedPath;

  return (
    <div className="image-picker">
      {label && (
        <label className="form-label" htmlFor={readOnly ? undefined : inputId}>
          {label}
        </label>
      )}

      <div
        className={[
          'image-picker__slot',
          shown && 'image-picker__slot--filled',
          (disabled || readOnly) && 'image-picker__slot--static',
        ]
          .filter(Boolean)
          .join(' ')}
      >
        {shown ? (
          <img
            className="image-picker__preview"
            src={shown}
            alt={label || 'Selected image'}
            onError={() => setFailedSrc(shown)}
          />
        ) : (
          <span className="image-picker__placeholder">
            <ImagePlus size={20} aria-hidden="true" />
            <span>{placeholder}</span>
          </span>
        )}

        {!readOnly && (
          <div className="image-picker__actions">
            <button
              type="button"
              className="image-picker__btn"
              onClick={openPicker}
              disabled={disabled}
            >
              {hasValue ? 'Replace' : 'Upload'}
            </button>
            {hasValue && onClear && (
              <button
                type="button"
                className="image-picker__btn image-picker__btn--danger"
                onClick={() => onClear()}
                disabled={disabled}
                title="Remove image"
                aria-label={`Remove ${label || 'image'}`}
              >
                <Trash2 size={14} aria-hidden="true" />
              </button>
            )}
          </div>
        )}
      </div>

      {!readOnly && (
        <input
          id={inputId}
          ref={inputRef}
          type="file"
          accept={accept}
          className="image-picker__input"
          onChange={handleFile}
          disabled={disabled}
        />
      )}
    </div>
  );
};

export default ImagePicker;
