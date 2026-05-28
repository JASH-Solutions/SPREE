const SearchBar = ({ value, onChange, placeholder }) => {
  return (
    <div className="search">
      <input
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
      />
      <span>Filtrar</span>
    </div>
  );
};

export default SearchBar;