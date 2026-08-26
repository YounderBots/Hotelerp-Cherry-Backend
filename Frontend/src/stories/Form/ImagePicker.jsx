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
}) => {
  const inputRef = useRef(null);
  const inputId = useId();

  // A File needs an object URL to preview; an already-stored image is just a
  // URL. Derived once per value and revoked when the value changes or the
  // component unmounts — calling URL.createObjectURL(file) inline in the JSX,
  // as the Rooms screen used to, leaked one blob per render.
  const preview = useMemo(
    () => (value instanceof File ? URL.createObjectURL(value) : value || null),
    [value],
  );

  useEffect(() => {
    if (!(value instanceof File) || !preview) return undefined;
    return () => URL.revokeObjectURL(preview);
  }, [value, preview]);

  // A stored path can fail to load (the uploads directory is not currently
  // exposed through the API gateway). Fall back to the empty-slot treatment
  // rather than leaving the browser's broken-image glyph in the layout.
  // Recording WHICH src failed means a new value clears the state on its own,
  // with no effect needed to reset it.
  const [failedSrc, setFailedSrc] = useState(null);
  const failed = !!preview && preview === failedSrc;
  const shown = failed ? null : preview;

  const handleFile = (e) => {
    const file = e.target.files?.[0];
    if (file) onChange?.(file);
    // Reset so picking the same file twice in a row still fires a change.
    e.target.value = '';
  };

  const openPicker = () => {
    if (!disabled && !readOnly) inputRef.current?.click();
  };

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
            <span>
              {failed ? 'Image unavailable' : readOnly ? 'No image' : 'Choose image'}
            </span>
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
              {preview ? 'Replace' : 'Upload'}
            </button>
            {preview && onClear && (
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
