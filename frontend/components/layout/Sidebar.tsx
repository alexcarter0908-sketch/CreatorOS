export default function Sidebar() {
  return (
    <aside className="w-64 h-screen bg-gray-900 text-white p-6">
      <h1 className="text-2xl font-bold text-blue-400">
        CreatorOS
      </h1>

      <nav className="mt-10">
        <ul className="space-y-4">
          <li>🏠 Dashboard</li>
          <li>📁 Projects</li>
          <li>📝 Scripts</li>
          <li>🖼️ Thumbnails</li>
          <li>🎬 Videos</li>
          <li>📈 SEO</li>
          <li>⚙️ Settings</li>
        </ul>
      </nav>
    </aside>
  );
}