import { useEffect, useState } from "react";
import {
  fetchTitles,
  createTitle,
  updateTitle,
  fetchTopGenres,
  fetchRecommendations
} from "./api";
import "./index.css";

const emptyForm = {
  show_id: "",
  content_type: "Movie",
  title: "",
  director: "",
  cast_members: "",
  country: "",
  date_added: "",
  release_year: "",
  rating: "",
  duration_raw: "",
  duration_value: "",
  duration_unit: "",
  listed_in: "",
  description: ""
};

function App() {
  const [titles, setTitles] = useState([]);
  const [genres, setGenres] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [targetTitle, setTargetTitle] = useState("");

  const [filters, setFilters] = useState({
    type: "",
    rating: "",
    country: "",
    title: ""
  });

  const [form, setForm] = useState(emptyForm);
  const [editId, setEditId] = useState(null);
  const [editForm, setEditForm] = useState({});

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadTitles(currentFilters = filters) {
    try {
      setLoading(true);
      setError("");
      const data = await fetchTitles(currentFilters);
      setTitles(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadGenres() {
    try {
      const data = await fetchTopGenres();
      setGenres(data);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadTitles();
    loadGenres();
  }, []);

  function handleFilterChange(e) {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  }

  async function handleFilterSubmit(e) {
    e.preventDefault();
    await loadTitles(filters);
  }

  async function handleResetFilters() {
    const cleared = { type: "", rating: "", country: "", title: "" };
    setFilters(cleared);
    await loadTitles(cleared);
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleCreate(e) {
    e.preventDefault();

    try {
      setError("");
      setSuccess("");

      const payload = {
        ...form,
        release_year: Number(form.release_year),
        duration_value: form.duration_value ? Number(form.duration_value) : null,
        date_added: form.date_added || null
      };

      await createTitle(payload);
      setSuccess("New record added successfully");
      setForm(emptyForm);
      await loadTitles();
      await loadGenres();
    } catch (err) {
      setError(err.message);
    }
  }

  function startEdit(item) {
    setEditId(item.show_id);
    setEditForm({
      content_type: item.content_type || "",
      title: item.title || "",
      director: item.director || "",
      cast_members: item.cast_members || "",
      country: item.country || "",
      date_added: item.date_added || "",
      release_year: item.release_year || "",
      rating: item.rating || "",
      duration_raw: item.duration_raw || "",
      duration_value: item.duration_value || "",
      duration_unit: item.duration_unit || "",
      listed_in: item.listed_in || "",
      description: item.description || ""
    });
  }

  function handleEditChange(e) {
    const { name, value } = e.target;
    setEditForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleUpdate(showId) {
    try {
      setError("");
      setSuccess("");

      const payload = {
        ...editForm,
        release_year: editForm.release_year ? Number(editForm.release_year) : null,
        duration_value: editForm.duration_value ? Number(editForm.duration_value) : null,
        date_added: editForm.date_added || null
      };

      await updateTitle(showId, payload);
      setSuccess(`Record ${showId} updated successfully`);
      setEditId(null);
      await loadTitles();
      await loadGenres();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleRecommendations(title) {
    try {
      setError("");
      const data = await fetchRecommendations(title);
      setTargetTitle(data.target_title);
      setRecommendations(data.recommendations);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page">
      <header className="header">
        <h1>Netflix Content Dashboard</h1>
        <p>Frontend dla projektu z przedmiotu „Systemy chmurowe”</p>
      </header>

      {error && <div className="message error">{error}</div>}
      {success && <div className="message success">{success}</div>}

      <section className="card">
        <h2>Filtrowanie danych</h2>
        <form className="grid-form" onSubmit={handleFilterSubmit}>
          <select name="type" value={filters.type} onChange={handleFilterChange}>
            <option value="">Wszystkie typy</option>
            <option value="Movie">Movie</option>
            <option value="TV Show">TV Show</option>
          </select>

          <input
            name="rating"
            placeholder="Rating"
            value={filters.rating}
            onChange={handleFilterChange}
          />

          <input
            name="country"
            placeholder="Country"
            value={filters.country}
            onChange={handleFilterChange}
          />

          <input
            name="title"
            placeholder="Title"
            value={filters.title}
            onChange={handleFilterChange}
          />

          <button type="submit">Filtruj</button>
          <button type="button" onClick={handleResetFilters}>Reset</button>
        </form>
      </section>

      <section className="card">
        <h2>Dodawanie nowego rekordu</h2>
        <form className="grid-form" onSubmit={handleCreate}>
          <input name="show_id" placeholder="show_id" value={form.show_id} onChange={handleFormChange} required />
          <select name="content_type" value={form.content_type} onChange={handleFormChange}>
            <option value="Movie">Movie</option>
            <option value="TV Show">TV Show</option>
          </select>
          <input name="title" placeholder="Title" value={form.title} onChange={handleFormChange} required />
          <input name="director" placeholder="Director" value={form.director} onChange={handleFormChange} />
          <input name="cast_members" placeholder="Cast members" value={form.cast_members} onChange={handleFormChange} />
          <input name="country" placeholder="Country" value={form.country} onChange={handleFormChange} />
          <input name="date_added" type="date" value={form.date_added} onChange={handleFormChange} />
          <input name="release_year" type="number" placeholder="Release year" value={form.release_year} onChange={handleFormChange} required />
          <input name="rating" placeholder="Rating" value={form.rating} onChange={handleFormChange} />
          <input name="duration_raw" placeholder="Duration raw" value={form.duration_raw} onChange={handleFormChange} />
          <input name="duration_value" type="number" placeholder="Duration value" value={form.duration_value} onChange={handleFormChange} />
          <input name="duration_unit" placeholder="Duration unit" value={form.duration_unit} onChange={handleFormChange} />
          <input name="listed_in" placeholder="Genres" value={form.listed_in} onChange={handleFormChange} />
          <textarea name="description" placeholder="Description" value={form.description} onChange={handleFormChange} required />
          <button type="submit">Dodaj rekord</button>
        </form>
      </section>

      <section className="layout">
        <div className="card wide">
          <h2>Lista rekordów</h2>
          {loading ? (
            <p>Ładowanie...</p>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>show_id</th>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Year</th>
                    <th>Rating</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {titles.map((item) => (
                    <tr key={item.show_id}>
                      <td>{item.show_id}</td>
                      <td>{item.title}</td>
                      <td>{item.content_type}</td>
                      <td>{item.release_year}</td>
                      <td>{item.rating}</td>
                      <td className="actions">
                        <button onClick={() => startEdit(item)}>Edit</button>
                        <button onClick={() => handleRecommendations(item.title)}>Recommend</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="card">
          <h2>Top genres</h2>
          <ul className="stats-list">
            {genres.map((item) => (
              <li key={item.genre}>
                <span>{item.genre}</span>
                <strong>{item.count}</strong>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {editId && (
        <section className="card">
          <h2>Edycja rekordu: {editId}</h2>
          <div className="grid-form">
            <select name="content_type" value={editForm.content_type} onChange={handleEditChange}>
              <option value="Movie">Movie</option>
              <option value="TV Show">TV Show</option>
            </select>
            <input name="title" value={editForm.title} onChange={handleEditChange} />
            <input name="director" value={editForm.director} onChange={handleEditChange} />
            <input name="cast_members" value={editForm.cast_members} onChange={handleEditChange} />
            <input name="country" value={editForm.country} onChange={handleEditChange} />
            <input name="date_added" type="date" value={editForm.date_added || ""} onChange={handleEditChange} />
            <input name="release_year" type="number" value={editForm.release_year || ""} onChange={handleEditChange} />
            <input name="rating" value={editForm.rating || ""} onChange={handleEditChange} />
            <input name="duration_raw" value={editForm.duration_raw || ""} onChange={handleEditChange} />
            <input name="duration_value" type="number" value={editForm.duration_value || ""} onChange={handleEditChange} />
            <input name="duration_unit" value={editForm.duration_unit || ""} onChange={handleEditChange} />
            <input name="listed_in" value={editForm.listed_in || ""} onChange={handleEditChange} />
            <textarea name="description" value={editForm.description || ""} onChange={handleEditChange} />
            <button onClick={() => handleUpdate(editId)}>Zapisz zmiany</button>
            <button onClick={() => setEditId(null)}>Anuluj</button>
          </div>
        </section>
      )}

      <section className="card">
        <h2>Recommendations</h2>
        {targetTitle ? <p>Podobne tytuły do: <strong>{targetTitle}</strong></p> : <p>Wybierz rekord z listy i kliknij „Recommend”.</p>}
        <div className="recommendations">
          {recommendations.map((item) => (
            <div className="recommendation-card" key={item.show_id}>
              <h3>{item.title}</h3>
              <p><strong>Type:</strong> {item.content_type}</p>
              <p><strong>Year:</strong> {item.release_year}</p>
              <p><strong>Rating:</strong> {item.rating}</p>
              <p><strong>Genres:</strong> {item.listed_in}</p>
              <p><strong>Score:</strong> {item.score}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default App;