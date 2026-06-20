"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

export default function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const [search, setSearch] = useState("");

  const isActive = (path: string) =>
    pathname === path ? "active" : "";

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (search.trim()) {
      router.push(`/browse?search=${encodeURIComponent(search.trim())}`);
      setSearch("");
    }
  };

  return (
    <header className="header">
      <div className="container header-inner">
        <Link href="/" className="logo">
          SCP-ARCHIVE <span>v1.0</span>
        </Link>

        <form className="search-bar" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Search SCPs, tales, GOIs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="btn btn-primary">
            SEARCH
          </button>
        </form>

        <nav className="nav-links">
          <Link href="/browse" className={isActive("/browse")}>
            BROWSE
          </Link>
          <Link href="/ai-guide" className={isActive("/ai-guide")}>
            AI GUIDE
          </Link>
          <Link href="/tags" className={isActive("/tags")}>
            TAGS
          </Link>
        </nav>
      </div>
    </header>
  );
}