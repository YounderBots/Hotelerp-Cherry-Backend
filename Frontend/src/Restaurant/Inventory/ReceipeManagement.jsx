import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, Ban, CheckCircle, Plus, X, Trash2 } from "lucide-react";
import "../../MasterData/MasterData.css";

const ReceipeManagement = () => {
  const [activeModal, setActiveModal] = useState(null); // addEdit | view
  const [selectedRecipe, setSelectedRecipe] = useState(null);

  /* ================= MOCK DATA ================= */
  const recipeData = [
    {
      id: 1,
      recipeCode: "REC102",
      menuItem: "Paneer Butter Masala",
      category: "Main Course",
      kitchen: "Main Kitchen",
      ingredientCount: "6 Ingredients",
      cost: "₹62.50",
      status: "Active",
      autoDeduct: "Yes",
      ingredients: [
        { name: "Paneer", qty: 0.2, unit: "Kg" },
        { name: "Butter", qty: 0.05, unit: "Kg" },
      ],
    },
    {
      id: 2,
      recipeCode: "REC118",
      menuItem: "Chicken Grill",
      category: "Starter",
      kitchen: "Grill",
      ingredientCount: "5 Ingredients",
      cost: "₹85.00",
      status: "Inactive",
      autoDeduct: "No",
      ingredients: [],
    },
  ];

  /* ================= MODAL HANDLERS ================= */
  const openModal = (type, row = null) => {
    setSelectedRecipe(row);
    setActiveModal(type);
  };

  const closeModal = () => {
    setSelectedRecipe(null);
    setActiveModal(null);
  };

  return (
    <> 

      {/* ================= RECIPE TABLE ================= */}
      <TableTemplate
        title="Recipes"
        searchable
        pagination
        columns={[
          { key: "recipeCode", title: "Recipe Code" },
          { key: "menuItem", title: "Menu Item" },
          { key: "category", title: "Category" },
          { key: "kitchen", title: "Kitchen Category" },
          { key: "ingredientCount", title: "Ingredients Count", align: "center" },
          { key: "cost", title: "Estimated Cost", align: "center" },
          {
            key: "status",
            title: "Status",
            type: "badge",
            align: "center",
          },
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  gap: 8,
                  flexWrap: "nowrap",
                }}
              >
                <button
                  className="table-action-btn view"
                  title="View"
                  onClick={() => openModal("view", row)}
                >
                  <Eye size={16} />
                </button>

                <button
                  className="table-action-btn edit"
                  title="Edit"
                  onClick={() => openModal("addEdit", row)}
                >
                  <Pencil size={16} />
                </button>

                {row.status === "Active" ? (
                  <button
                    className="table-action-btn delete"
                    title="Disable"
                  >
                    <Ban size={16} />
                  </button>
                ) : (
                  <button
                    className="table-action-btn edit"
                    title="Enable"
                  >
                    <CheckCircle size={16} />
                  </button>
                )}
              </div>
            ),
          },
        ]}
        data={recipeData}
      />

      {/* ================= ADD / EDIT MODAL ================= */}
      {activeModal === "addEdit" && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: 1000 }}>
            <div className="modal-header">
              <h3>Add / Edit Recipe</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              {/* Header */}
              <div className="row g-3 mb-3">
                <div className="col-md-3">
                  <label>Recipe Code</label>
                  <input value={selectedRecipe?.recipeCode || ""} />
                </div>

                <div className="col-md-5">
                  <label>Menu Item</label>
                  <select>
                    <option>Paneer Butter Masala</option>
                  </select>
                </div>

                <div className="col-md-4">
                  <label>Kitchen Category</label>
                  <select>
                    <option>Main Kitchen</option>
                  </select>
                </div>
              </div>

              {/* Ingredients */}
              <h6 className="fw-semibold mb-2">Ingredients Mapping</h6>

              <table className="table table-sm table-bordered">
                <thead>
                  <tr>
                    <th>Ingredient</th>
                    <th>Store</th>
                    <th>Qty</th>
                    <th>Unit</th>
                    <th>Wastage %</th>
                    <th>Cost</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Paneer</td>
                    <td>Kitchen Store</td>
                    <td>0.2</td>
                    <td>Kg</td>
                    <td>5</td>
                    <td>₹40</td>
                    <td style={{ textAlign: "center" }}>
                      <button className="btn icon">
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>

              <button className="btn secondary mb-3">
                <Plus size={14} /> Add Ingredient
              </button>

              {/* Controls */}
              <div className="row g-3">
                <div className="col-md-3">
                  <label>Auto Deduct Stock</label>
                  <select>
                    <option>Yes</option>
                    <option>No</option>
                  </select>
                </div>

                <div className="col-md-3">
                  <label>Allow Partial Deduction</label>
                  <select>
                    <option>Yes</option>
                    <option>No</option>
                  </select>
                </div>

                <div className="col-md-3 d-flex align-items-center">
                  <label className="mt-4">
                    <input type="checkbox" defaultChecked /> Active
                  </label>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>
                Cancel
              </button>
              <button className="btn primary">
                Save Recipe
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= VIEW MODAL ================= */}
      {activeModal === "view" && selectedRecipe && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: 600 }}>
            <div className="modal-header">
              <h3>Recipe Details – {selectedRecipe.menuItem}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <p><strong>Kitchen:</strong> {selectedRecipe.kitchen}</p>
              <p><strong>Estimated Cost:</strong> {selectedRecipe.cost}</p>
              <p><strong>Auto Deduct:</strong> {selectedRecipe.autoDeduct}</p>

              <table className="table table-sm mt-3">
                <thead>
                  <tr>
                    <th>Ingredient</th>
                    <th>Qty</th>
                    <th>Unit</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedRecipe.ingredients.map((i, idx) => (
                    <tr key={idx}>
                      <td>{i.name}</td>
                      <td>{i.qty}</td>
                      <td>{i.unit}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ReceipeManagement;
