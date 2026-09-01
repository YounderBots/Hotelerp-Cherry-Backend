import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal, { ConfirmModal } from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import Button from "../../stories/Button";
import ErrorAlert from "../../stories/ErrorAlert";
import RowActions from "../../stories/RowActions";
import Textarea from "../../stories/Form/Textarea";
import ImagePicker from "../../stories/Form/ImagePicker";
import Toast from "../../stories/Toast";
import DetailList, { DetailItem } from "../../stories/DetailList";
import { ChipGroup } from "../../stories/Chip";
import ViewSection from "../../stories/ViewSection";
import RepeatableRowEditor from "../../stories/RepeatableRowEditor";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { formatPrecise } from "../../functions/formatters";
import { useApiResources } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";
import "../../stories/menuModalFields.css";

const readOne = (res) => (res?.data && typeof res.data === "object" && !Array.isArray(res.data) ? res.data : null);

const MODIFIER_TYPES = ["Add-on", "Remove"];
const VARIANT_SUGGESTIONS = ["30ml", "60ml", "90ml", "Glass", "Bottle", "Pint"];

const emptyVariant = () => ({ variant_name: "", price: "" });
const emptyModifier = () => ({ modifier_name: "", price: "", modifier_type: "Add-on" });

const initialForm = {
  item_name: "",
  description: "",
  category_id: "",
  sub_category_id: "",
  station_id: "",
  preparation_time: "",
  price: "",
  cost_price: "",
  tax_percentage: "",
  service_charge_applicable: false,
  availability_status: "Available",
  happy_hour_eligible: false,
  dietary_tags: "",
  item_image: "",
};

/**
 * A stored menu photo, fetched with the session token.
 *
 * Uploads sit behind the authenticated gateway proxy, so a plain <img src> is
 * answered 401. ImagePicker already knows how to fetch one (`authPrefix`), so
 * the thumbnail is that component in read-only mode rather than a second
 * implementation. Items saved before this screen had an uploader hold an
 * external absolute URL; useAuthedMedia passes those through untouched.
 */
const MenuThumb = ({ path, alt, size = "cell" }) => {
  if (!path) return "—";
  return (
    <span className={`menu-thumb menu-thumb--${size}`}>
      <ImagePicker value={path} authPrefix="/bar" label={alt} readOnly />
    </span>
  );
};

const MenuManagement = () => {
  const perms = usePagePermissions("/bar_menus");
  const { toast, showToast } = useToast();
  const [deleteRow, setDeleteRow] = useState(null);
  const [imageUploading, setImageUploading] = useState(false);
  // Was four setStates driven by a hand-rolled Promise.allSettled inside a
  // useCallback + useEffect pair — the shape useApiResources owns.
  const {
    data: [data, categories, subCategories, stations],
    loading,
    error,
    reload: load,
  } = useApiResources([
    {
      fetch: () => APICall.getT("/bar/menu"),
      select: readList,
      fallback: "Failed to load menu items.",
    },
    { fetch: () => APICall.getT("/bar/menu_category"), select: readList },
    { fetch: () => APICall.getT("/bar/menu_sub_category"), select: readList },
    { fetch: () => APICall.getT("/bar/station"), select: readList },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [viewLoading, setViewLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const [formData, setFormData] = useState(initialForm);
  const [variants, setVariants] = useState([]);
  const [modifiers, setModifiers] = useState([]);
  const [existingDetail, setExistingDetail] = useState(null);
  const [newVariant, setNewVariant] = useState(emptyVariant());
  const [newModifier, setNewModifier] = useState(emptyModifier());

  // An unknown id reads as "—": a row number tells the user nothing, and
  // usually just means the reference list has not loaded.
  const categoryName = (id) => categories.find((c) => c.id === id)?.category_name || "—";
  const subCategoryName = (id) => subCategories.find((s) => s.id === id)?.sub_category_name || null;
  const stationName = (id) => stations.find((s) => s.id === id)?.station_name || "—";
  const subCategoryOptions = formData.category_id
    ? subCategories.filter((s) => Number(s.category_id) === Number(formData.category_id))
    : [];

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setVariants([]);
    setModifiers([]);
    setExistingDetail(null);
    setNewVariant(emptyVariant());
    setNewModifier(emptyModifier());
    setFormError(null);
    setShowModal(true);
  };

  const openViewModal = async (row) => {
    setShowViewModal(true);
    setViewLoading(true);
    setViewData({ ...row });
    try {
      const res = await APICall.getT(`/bar/menu/${row.id}`);
      const detail = readOne(res);
      if (detail) setViewData(detail);
    } catch {
      // Detail fetch failed — the row data from the list is still shown.
    } finally {
      setViewLoading(false);
    }
  };
  const closeViewModal = () => {
    setViewData(null);
    setShowViewModal(false);
  };

  const closeModal = () => {
    if (saving) return;
    setEditId(null);
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value, ...(name === "category_id" ? { sub_category_id: "" } : {}) }));
  };

  const handleBoolChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value === "true" }));
  };

  const resolveCategoryId = () =>
    formData.category_id ? Number(formData.category_id) : null;

  const resolveSubCategoryId = () =>
    formData.sub_category_id ? Number(formData.sub_category_id) : null;

  const addVariant = () => setVariants((v) => [...v, emptyVariant()]);
  const updateVariant = (idx, field, value) =>
    setVariants((v) => v.map((row, i) => (i === idx ? { ...row, [field]: value } : row)));
  const removeVariant = (idx) => setVariants((v) => v.filter((_, i) => i !== idx));

  const addModifier = () => setModifiers((m) => [...m, emptyModifier()]);
  const updateModifier = (idx, field, value) =>
    setModifiers((m) => m.map((row, i) => (i === idx ? { ...row, [field]: value } : row)));
  const removeModifier = (idx) => setModifiers((m) => m.filter((_, i) => i !== idx));

  const refreshExistingDetail = async () => {
    try {
      const res = await APICall.getT(`/bar/menu/${editId}`);
      const detail = readOne(res);
      if (detail) setExistingDetail(detail);
    } catch {
      // Non-fatal — the modal stays open with the last-known list.
    }
  };

  const updateExistingVariantField = (id, field, value) =>
    setExistingDetail((d) => ({ ...d, variants: (d.variants || []).map((v) => (v.id === id ? { ...v, [field]: value } : v)) }));
  const saveExistingVariant = async (v) => {
    try {
      await APICall.putT(`/bar/variant/${v.id}`, { variant_name: v.variant_name, price: Number(v.price) });
      refreshExistingDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to update variant."));
    }
  };
  const deleteExistingVariant = async (id) => {
    try {
      await APICall.deleteT(`/bar/variant/${id}`);
      refreshExistingDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to delete variant."));
    }
  };
  const addExistingVariant = async () => {
    if (!newVariant.variant_name.trim() || newVariant.price === "") return;
    try {
      await APICall.postT(`/bar/menu/${editId}/variant`, {
        variant_name: newVariant.variant_name.trim(),
        price: Number(newVariant.price),
      });
      setNewVariant(emptyVariant());
      refreshExistingDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to add variant."));
    }
  };

  const updateExistingModifierField = (id, field, value) =>
    setExistingDetail((d) => ({ ...d, modifiers: (d.modifiers || []).map((m) => (m.id === id ? { ...m, [field]: value } : m)) }));
  const saveExistingModifier = async (m) => {
    try {
      await APICall.putT(`/bar/modifier/${m.id}`, {
        modifier_name: m.modifier_name,
        price: m.price !== "" && m.price != null ? Number(m.price) : null,
        modifier_type: m.modifier_type,
      });
      refreshExistingDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to update modifier."));
    }
  };
  const deleteExistingModifier = async (id) => {
    try {
      await APICall.deleteT(`/bar/modifier/${id}`);
      refreshExistingDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to delete modifier."));
    }
  };
  const addExistingModifier = async () => {
    if (!newModifier.modifier_name.trim()) return;
    try {
      await APICall.postT(`/bar/menu/${editId}/modifier`, {
        modifier_name: newModifier.modifier_name.trim(),
        price: newModifier.price !== "" ? Number(newModifier.price) : null,
        modifier_type: newModifier.modifier_type,
      });
      setNewModifier(emptyModifier());
      refreshExistingDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to add modifier."));
    }
  };

  const handleSave = async () => {
    if (!formData.item_name.trim() || !formData.price || !formData.category_id) {
      setFormError("Item name, price and category are required.");
      return;
    }
    const cleanVariants = variants.filter((v) => v.variant_name.trim() && v.price !== "");
    const cleanModifiers = modifiers.filter((m) => m.modifier_name.trim());
    setFormError(null);
    setSaving(true);
    try {
      const categoryId = resolveCategoryId();
      if (!categoryId) {
        setFormError("Could not resolve a category for this item.");
        setSaving(false);
        return;
      }
      const subCategoryId = resolveSubCategoryId();
      const dietaryTags = formData.dietary_tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);

      const basePayload = {
        item_name: formData.item_name.trim(),
        description: formData.description || null,
        category_id: categoryId,
        sub_category_id: subCategoryId || null,
        station_id: formData.station_id ? Number(formData.station_id) : null,
        preparation_time: formData.preparation_time ? Number(formData.preparation_time) : null,
        price: Number(formData.price),
        cost_price: formData.cost_price ? Number(formData.cost_price) : null,
        tax_percentage: formData.tax_percentage ? Number(formData.tax_percentage) : null,
        service_charge_applicable: formData.service_charge_applicable,
        availability_status: formData.availability_status,
        happy_hour_eligible: formData.happy_hour_eligible,
        dietary_tags: dietaryTags,
        item_image: formData.item_image || null,
      };

      if (editId) {
        await APICall.putT(`/bar/menu/${editId}`, basePayload);
      } else {
        await APICall.postT("/bar/menu", {
          ...basePayload,
          variants: cleanVariants.map((v) => ({ variant_name: v.variant_name.trim(), price: Number(v.price) })),
          modifiers: cleanModifiers.map((m) => ({
            modifier_name: m.modifier_name.trim(),
            price: m.price !== "" ? Number(m.price) : null,
            modifier_type: m.modifier_type,
          })),
        });
      }
      setShowModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save menu item."));
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = async (row) => {
    setEditId(row.id);
    setFormError(null);
    setVariants([]);
    setModifiers([]);
    setExistingDetail(null);
    setNewVariant(emptyVariant());
    setNewModifier(emptyModifier());
    setFormData({
      item_name: row.item_name || "",
      description: row.description || "",
      category_id: row.category_id ?? "",
      sub_category_id: row.sub_category_id ?? "",
      station_id: row.station_id ?? "",
      preparation_time: row.preparation_time ?? "",
      price: row.price ?? "",
      cost_price: row.cost_price ?? "",
      tax_percentage: row.tax_percentage ?? "",
      service_charge_applicable: !!row.service_charge_applicable,
      availability_status: row.availability_status || "Available",
      happy_hour_eligible: !!row.happy_hour_eligible,
      dietary_tags: Array.isArray(row.dietary_tags) ? row.dietary_tags.join(", ") : "",
      item_image: row.item_image || "",
    });
    setShowModal(true);
    try {
      const res = await APICall.getT(`/bar/menu/${row.id}`);
      const detail = readOne(res);
      if (detail) setExistingDetail(detail);
    } catch {
      // Non-fatal — the rest of the form still works without this.
    }
  };

  // Was wired straight to the trash icon: one click took an item off the menu
  // with no confirmation and no feedback.
  const confirmDelete = async () => {
    const row = deleteRow;
    setDeleteRow(null);
    try {
      await APICall.deleteT(`/bar/menu/${row.id}`);
      showToast("Menu item deactivated successfully", "delete");
      load();
    } catch (err) {
      showToast(errMsg(err, "Failed to deactivate menu item."), "error");
    }
  };

  // The bar had no upload endpoint, so this screen asked the user to paste a
  // hosted image URL while the identical restaurant screen offered a picker.
  // BarServices now has POST /bar/upload_image.
  const handleImageFile = async (file) => {
    if (!file) return;
    setImageUploading(true);
    setFormError(null);
    try {
      const body = new FormData();
      body.append("image", file);
      const res = await APICall.postT("/bar/upload_image", body);
      const url = res?.data?.url;
      if (url) setFormData((p) => ({ ...p, item_image: url }));
    } catch (err) {
      setFormError(errMsg(err, "Failed to upload image."));
    } finally {
      setImageUploading(false);
    }
  };

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Bar Menu Management"
        emptyMessage="No menu items yet. Add the first one to get started."
        hasActionButton={perms.add}
        searchable
        pagination
        exportable
        loading={loading}
        actionButton={{ label: "Add Item", onClick: openAddModal, size: "medium", variant: "primary" }}
        columns={[
          { key: "item_code", title: "Item Code", align: "center" },
          {
            key: "item_image",
            title: "Item",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => <MenuThumb path={row.item_image} alt={row.item_name} />,
          },
          { key: "item_name", title: "Item Name" },
          { key: "category_id", title: "Category", type: "custom", render: (row) => categoryName(row.category_id) },
          { key: "station_id", title: "Station", type: "custom", render: (row) => stationName(row.station_id) },
          {
            key: "price",
            title: "Price",
            align: "right",
            type: "custom",
            render: (row) => formatPrecise(row.price),
            exportValue: (row) => formatPrecise(row.price),
          },
          {
            key: "variants",
            title: "Variants",
            align: "center",
            type: "custom",
            render: (row) => (row.variants?.length ? `${row.variants.length} option${row.variants.length > 1 ? "s" : ""}` : "—"),
          },
          { key: "availability_status", title: "Availability", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <RowActions
                label={row.item_name || "menu item"}
                canEdit={perms.edit}
                canDelete={perms.delete}
                onView={() => openViewModal(row)}
                onEdit={() => handleEdit(row)}
                onDelete={() => setDeleteRow(row)}
              />
            ),
          },
        ]}
        data={data}
      />

      {showViewModal && viewData && (
        <Modal
          isOpen={showViewModal}
          className="menu-view-modal"
          title={viewData.item_name}
          onClose={closeViewModal}
          size="large"
          bodyLayout="single"
          viewMode
          showFooter
          actions={[{ label: "Close", variant: "secondary", onClick: closeViewModal }]}
        >
          {viewData.item_image && (
            <div className="menu-view__hero">
              <MenuThumb path={viewData.item_image} alt={viewData.item_name} size="hero" />
            </div>
          )}

          <ViewSection title="Basic Information">
            {/* Every field here used to be an `<Input ... disabled />` — a form
                control the user could tab into, with a "switched off" border,
                which is exactly what DetailList was written to replace. */}
            <DetailList columns={2}>
              <DetailItem label="Item Code" value={viewData.item_code} />
              <DetailItem label="Category" value={categoryName(viewData.category_id)} />
              <DetailItem label="Sub-Category" value={subCategoryName(viewData.sub_category_id)} />
              <DetailItem label="Station" value={stationName(viewData.station_id)} />
              <DetailItem label="Description" value={viewData.description} span={2} />
            </DetailList>
          </ViewSection>

          <ViewSection title="Pricing">
            <DetailList columns={2}>
              <DetailItem label="Price" value={formatPrecise(viewData.price)} />
              <DetailItem label="Cost Price" value={formatPrecise(viewData.cost_price)} />
              <DetailItem label="Tax %" value={viewData.tax_percentage ?? 0} />
              <DetailItem
                label="Service Charge Applicable"
                value={viewData.service_charge_applicable ? "Yes" : "No"}
              />
            </DetailList>
          </ViewSection>

          <ViewSection title="Attributes">
            <DetailList columns={2}>
              <DetailItem label="Availability" value={viewData.availability_status} />
              <DetailItem
                label="Happy Hour Eligible"
                value={viewData.happy_hour_eligible ? "Yes" : "No"}
              />
              <DetailItem
                label="Preparation Time"
                value={viewData.preparation_time ? `${viewData.preparation_time} min` : null}
              />
              {(viewData.dietary_tags || []).length > 0 && (
                <DetailItem label="Dietary Tags" span={2}>
                  <ChipGroup items={viewData.dietary_tags} />
                </DetailItem>
              )}
            </DetailList>
          </ViewSection>

          {(viewData.variants?.length > 0 || viewData.modifiers?.length > 0) && (
            <ViewSection title="Variants & Modifiers">
              <ChipGroup
                items={[
                  ...(viewData.variants || []).map((v) => ({ key: `v-${v.id}`, label: `${v.variant_name} — ${formatPrecise(v.price)}` })),
                  ...(viewData.modifiers || []).map((m) => ({
                    key: `m-${m.id}`,
                    label: `${m.modifier_name} (${m.modifier_type})${m.price ? ` — ${formatPrecise(m.price)}` : ""}`,
                  })),
                ]}
              />
            </ViewSection>
          )}

          {viewLoading && <p className="repeatable-empty">Loading full details…</p>}
        </Modal>
      )}

      {showModal && (
        <Modal
          isOpen={showModal}
          className="menu-modal"
          title={editId ? "Edit Menu Item" : "Add Menu Item"}
          onClose={closeModal}
          size="large"
          bodyLayout="grid"
          showFooter
          actions={[
            { label: "Close", variant: "secondary", onClick: closeModal, disabled: saving },
            { label: saving ? "Saving…" : "Submit", variant: "primary", onClick: handleSave, disabled: saving },
          ]}
        >
          {formError && (
            <div className="field-full">
              <ErrorAlert message={formError} />
            </div>
          )}

          <Input label="Item Name" required name="item_name" value={formData.item_name} onChange={handleChange} />

          <Select
            label="Category"
            required
            name="category_id"
            value={formData.category_id}
            onChange={handleChange}
            options={categories.map((c) => ({ value: c.id, label: c.category_name }))}
            placeholder="— select —"
          />

          <Select
            label="Sub-Category"
            name="sub_category_id"
            value={formData.sub_category_id}
            onChange={handleChange}
            disabled={!formData.category_id}
            options={subCategoryOptions.map((s) => ({ value: s.id, label: s.sub_category_name }))}
            placeholder={formData.category_id ? "— select —" : "Select a category first"}
          />

          <Select
            label="Station"
            name="station_id"
            value={formData.station_id}
            onChange={handleChange}
            options={stations.map((s) => ({ value: s.id, label: s.station_name }))}
            placeholder="— select —"
          />

          <Input label="Preparation Time (min)" type="number" name="preparation_time" value={formData.preparation_time} onChange={handleChange} />

          <Input label="Price" required type="number" name="price" value={formData.price} onChange={handleChange} />

          <Input label="Cost Price" type="number" name="cost_price" value={formData.cost_price} onChange={handleChange} />

          <Input label="Tax %" type="number" name="tax_percentage" value={formData.tax_percentage} onChange={handleChange} />

          <Select
            label="Service Charge Applicable"
            name="service_charge_applicable"
            value={String(formData.service_charge_applicable)}
            onChange={handleBoolChange}
            options={[{ value: "false", label: "No" }, { value: "true", label: "Yes" }]}
          />

          <Select
            label="Availability"
            name="availability_status"
            value={formData.availability_status}
            onChange={handleChange}
            options={[{ value: "Available", label: "Available" }, { value: "Out of Stock", label: "Out of Stock" }]}
          />

          <Select
            label="Happy Hour Eligible"
            name="happy_hour_eligible"
            value={String(formData.happy_hour_eligible)}
            onChange={handleBoolChange}
            options={[{ value: "false", label: "No" }, { value: "true", label: "Yes" }]}
          />

          <div className="field-full">
            <Input label="Description" name="description" value={formData.description} onChange={handleChange} />
          </div>

          <div className="field-full">
            <Input
              label="Dietary Tags (comma-separated, e.g. Alcoholic, Non-Alcoholic)"
              name="dietary_tags"
              value={formData.dietary_tags}
              onChange={handleChange}
              placeholder="Alcoholic, Non-Alcoholic"
            />
          </div>

          <div className="field-full">
            {/* Was "paste a hosted image URL" into a text box, while the
                identical restaurant screen offered a file picker. */}
            <ImagePicker
              label={imageUploading ? "Item Image — uploading…" : "Item Image"}
              value={formData.item_image}
              authPrefix="/bar"
              disabled={imageUploading}
              onChange={handleImageFile}
              onClear={() => setFormData((p) => ({ ...p, item_image: "" }))}
            />
          </div>

          {!editId && (
            <div className="field-full">
              <label className="form-label">Variants (e.g. 30ml / 60ml / 90ml pricing)</label>
              <RepeatableRowEditor
                rows={variants}
                fields={[
                  { key: "variant_name", placeholder: "Variant name (e.g. Large)", listId: "variant-suggestions" },
                  { key: "price", placeholder: "Price", type: "number" },
                ]}
                onFieldChange={(index, key, value) => updateVariant(index, key, value)}
                onAdd={addVariant}
                onRemove={(index) => removeVariant(index)}
                addLabel="+ Add Variant"
                emptyLabel="No variants — this item will use the single price above."
              />
              <datalist id="variant-suggestions">
                {VARIANT_SUGGESTIONS.map((s) => (
                  <option key={s} value={s} />
                ))}
              </datalist>
            </div>
          )}

          {!editId && (
            <div className="field-full">
              <label className="form-label">Modifiers (add-ons or removable ingredients)</label>
              <RepeatableRowEditor
                rows={modifiers}
                fields={[
                  { key: "modifier_name", placeholder: "Modifier name (e.g. On the Rocks)" },
                  { key: "price", placeholder: "Price", type: "number" },
                  { key: "modifier_type", placeholder: "Type", type: "select", options: MODIFIER_TYPES },
                ]}
                onFieldChange={(index, key, value) => updateModifier(index, key, value)}
                onAdd={addModifier}
                onRemove={(index) => removeModifier(index)}
                addLabel="+ Add Modifier"
                emptyLabel="No modifiers for this item."
              />
            </div>
          )}

          {editId && existingDetail && (
            <div className="field-full">
              <label className="form-label">Variants (e.g. 30ml / 60ml / 90ml pricing)</label>
              <RepeatableRowEditor
                rows={existingDetail.variants || []}
                fields={[
                  { key: "variant_name", placeholder: "Variant name" },
                  { key: "price", placeholder: "Price", type: "number" },
                ]}
                onFieldChange={(index, key, value, row) => updateExistingVariantField(row.id, key, value)}
                onRemove={(index, row) => deleteExistingVariant(row.id)}
                renderRowExtra={(row) => (
                  <Button variant="secondary" size="small" onClick={() => saveExistingVariant(row)}>
                    Save
                  </Button>
                )}
                emptyLabel="No variants — this item uses the single price above."
                rowKey={(row) => row.id}
              />
              <div className="menu-inline-add">
                <Input
                  placeholder="Variant name (e.g. Large)"
                  value={newVariant.variant_name}
                  onChange={(e) => setNewVariant((p) => ({ ...p, variant_name: e.target.value }))}
                />
                <Input
                  placeholder="Price"
                  type="number"
                  value={newVariant.price}
                  onChange={(e) => setNewVariant((p) => ({ ...p, price: e.target.value }))}
                />
                <Button variant="secondary" onClick={addExistingVariant}>+ Add Variant</Button>
              </div>
            </div>
          )}

          {editId && existingDetail && (
            <div className="field-full">
              <label className="form-label">Modifiers (add-ons or removable ingredients)</label>
              <RepeatableRowEditor
                rows={existingDetail.modifiers || []}
                fields={[
                  { key: "modifier_name", placeholder: "Modifier name" },
                  { key: "price", placeholder: "Price", type: "number" },
                  { key: "modifier_type", placeholder: "Type", type: "select", options: MODIFIER_TYPES },
                ]}
                onFieldChange={(index, key, value, row) => updateExistingModifierField(row.id, key, value)}
                onRemove={(index, row) => deleteExistingModifier(row.id)}
                renderRowExtra={(row) => (
                  <Button variant="secondary" size="small" onClick={() => saveExistingModifier(row)}>
                    Save
                  </Button>
                )}
                emptyLabel="No modifiers for this item."
                rowKey={(row) => row.id}
              />
              <div className="menu-inline-add">
                <Input
                  placeholder="Modifier name (e.g. Extra Shot)"
                  value={newModifier.modifier_name}
                  onChange={(e) => setNewModifier((p) => ({ ...p, modifier_name: e.target.value }))}
                />
                <Input
                  placeholder="Price"
                  type="number"
                  value={newModifier.price}
                  onChange={(e) => setNewModifier((p) => ({ ...p, price: e.target.value }))}
                />
                <Select
                  value={newModifier.modifier_type}
                  onChange={(e) => setNewModifier((p) => ({ ...p, modifier_type: e.target.value }))}
                  options={MODIFIER_TYPES}
                  fullWidth={false}
                />
                <Button variant="secondary" onClick={addExistingModifier}>+ Add Modifier</Button>
              </div>
            </div>
          )}
        </Modal>
      )}

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteRow}
        onClose={() => setDeleteRow(null)}
        onConfirm={confirmDelete}
        title="Deactivate Menu Item"
        confirmText="Deactivate"
        size="small"
        destructive
      >
        {`Deactivate ${deleteRow?.item_name || "this item"}? It will no longer be orderable.`}
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default MenuManagement;
