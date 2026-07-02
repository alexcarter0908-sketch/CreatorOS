export default function Navbar() {
  return (
    <header className="flex items-center justify-between bg-white border-b px-8 py-4">
      <div>
        <h2 className="text-2xl font-bold">Dashboard</h2>
        <p className="text-gray-500 text-sm">
          Welcome back to CreatorOS
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold">
          100 Credits
        </div>

        <div className="w-10 h-10 rounded-full bg-gray-300"></div>
      </div>
    </header>
  );
}